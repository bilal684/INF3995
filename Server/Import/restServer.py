#!/usr/bin/python3
from flask import Flask, Response, send_file, request, send_file
from lxml import etree as ET
from os import listdir
from os.path import isfile, join
import  os.path, sys, hashlib, binascii
from PyQt5 import QtCore
import logging
import os
import json
import datetime
import time


# ----------------------------------------CLASS----------------------------------------------#
# Classe RestServer dérivée de la classe QtCore.Thread
# Elle permet d'encapsuler les méthodes utilisées par le thread responsable de l'établissement
# d'une connexion avec les clients Android, de l'envoi de fichiers et d'informations aux clients
# connectés. Il s'agit du serveur REST
# -------------------------------------------------------------------------------------------#
class RestServer(QtCore.QThread):
	
	DispayLogMessage = QtCore.pyqtSignal(str)
	app = None
	
	def __init__(self, host, connectedUsers):
		QtCore.QThread.__init__(self)
		self.connectedUsersFileName = "./Account/connectedUsers.xml"
		self.dataBaseFileName = "./Account/accounts.xml"
		self.pathToRocketsConfig = "./config/rockets"
		self.pathToMiscFiles = "./config/miscFiles"
		self.configXml = "./config/config.xml"
		self.host = host
		self.connectedUsers = connectedUsers
		self.app = Flask(__name__)

		
	#Fonction permettant de démarrer le serveur. Au démarrage, elle supprime
	#le fichier contenant les utilisateurs connectés de la dernière session.
	def run(self):
		
		#Methode permettant la connection d'un utilisateur. Elle vérifie le nom d'utilisateur et le
		#mot de passe, dans le cas d'un nom d'utilisateur et d'un mot de passe valide, elle retourne
		#200 et un token qui devra être utilisé par l'application mobile pour les services REST.
		#Sinon, elle retourne 401 dans le cas où le fichier contenant les comptes utilisateurs
		#et mot de passe n'existe pas, dans le cas où le nom d'utilisateur ou le mot de passe est
		#invalide.
		@self.app.route("/users/login", methods=['POST'])
		def login():
			#Si la base de donnée contenant les comptes n'existe pas...
			if not os.path.exists(self.dataBaseFileName):
				self.logger("error@Database file '"+ self.dataBaseFileName + "' was not found.")
				return Response("Database file '"+ self.dataBaseFileName + "' was not found."), 401
			else:
				#Lire la base de donnée contenant les comptes.
				parser = ET.XMLParser(remove_blank_text=True)
				tree = ET.parse(self.dataBaseFileName, parser)
				root = tree.getroot()
				request_json = request.get_json()
				givenUsername = request_json.get('username').lower()
				givenPassword = request_json.get('password')
				user = root.find(givenUsername)
				#Si le compte utilisateur existe.
				if user is not None:
					userPassword = user.find('password')
					#Verifier si le mot de passe est valide
					if(userPassword.text == self.encryptPassword(givenPassword).decode('ascii')):
						token = givenUsername + ':' + userPassword.text[:10]
						
						userObject = (givenUsername, request.remote_addr, request.headers.get('User-Agent').split(';')[2], datetime.datetime.now())
						#Si le fichier contenant les utilisateurs connectés n'existe pas, on va le créer.
						if not os.path.exists(self.connectedUsersFileName):
							root = ET.Element('ConnectedUsers')
							self.createConnectedUserEntry(root, givenUsername, token)
							self.logger("info@User " + givenUsername + " sucessfully authenticated")
							self.connectedUsers.append(userObject)
						else:
							#Si le fichier contenant les utilisateurs connectés existe
							parser = ET.XMLParser(remove_blank_text=True)
							tree = ET.parse(self.connectedUsersFileName, parser)
							root = tree.getroot()
							#Si le username n'est pas dans le fichier des utilisateurs connectés
							if root.find(givenUsername) is None:
								self.createConnectedUserEntry(root, givenUsername, token)
								self.logger("info@User " + givenUsername + " sucessfully authenticated")
								self.connectedUsers.append(userObject)
							else:
								self.logger("warn@Username "  + givenUsername + " attempted to login while already logged in.")
								return Response("User already logged in"), 403
						return Response(token), 200
					else:
						#Avertir de l'échec de la tentative de connexion.
						self.logger("warn@Username "  + givenUsername + " attempted to login with an invalid password")
						return Response("Given password is invalid"), 401
				else:
					#Avertir que le compte utilisateur n'existe pas et refuser l'accès
					self.logger("warn@Username " + givenUsername + " was not found in " + self.dataBaseFileName)
					return Response("Username " + givenUsername + " does not exist"), 401

		#Methode permettant la déconnexion d'un utilisateur. L'utilisateur devra envoyé son nom d'utilisateur
		#dans un JSON et son token en argument. Le token doit être envoyé pour des mesures de sécurité afin
		#d'éviter que n'importe qui déconnecte les utilisateurs. Elle retourne 200 lorsque la déconnexion
		#se fait avec succès. 400 lorsque la requête ne contient pas l'argument token et 401 si l'utilisateur
		#n'est pas authentifier ou lorsque le fichier contenant les utilisateurs connectés n'existe pas.
		@self.app.route("/users/logout", methods=['POST'])
		def logout():
			token = request.args.get('token')
			#Si le token n'a pas été fourni en argument.
			if token is None:
				self.logger("warn@Request for basic config received no token.")
				return Response("Malformed request, token argument does not exist."), 400
			isAuthenticated = self.checkIfTokenValid(token)
			#Si l'utilisateur n'est pas authentifier, retourne 401.
			if not isAuthenticated:
				self.logger("warn@User " + token.split(':')[0] + " failed to log out")
				return Response("Failed to log out user"), 401
			else:
				#Si l'utilisateur était authentifier, on procède à sa déconnexion.
				parser = ET.XMLParser(remove_blank_text=True)
				tree = ET.parse(self.connectedUsersFileName, parser)
				root = tree.getroot()
				request_json = request.get_json()
				givenUsername = request_json.get('username').lower()
				user = root.find(givenUsername) #Ici, il va nécessairement le trouver, car on a valider qu'il était authentifié
				root.remove(user)
				tree = ET.ElementTree(root)
				tree.write(self.connectedUsersFileName, pretty_print=True, xml_declaration=True, encoding="utf-8")
				self.logger("info@User " + givenUsername + " logged out.")
				for conn in self.connectedUsers:
					if conn[0] == givenUsername:
						self.connectedUsers.remove(conn)
				return Response("Username " + givenUsername + " logged out."), 200
				#Unreachable code
				#else:
				#    self.log("Username " + givenUsername + " attempted to log out when it was already logged out.", "WARNING")
				#    return Response("Username " + givenUsername + " already logged out."), 401

		#Methode permettant de retourner à l'utilisateur la configuration de base. Il faut lui fournir
		#un token en paramètre qui va être validé. Elle retourne 400 lorsque n'a pas été fourni, 200 
		#et la configuration de base si l'utilisateur est authentifié, 404 lorsque le fichier de config
		#de base est inexistant et 401 si l'utilisateur n'est pas authentifié. 
		@self.app.route("/config/basic", methods=['GET'])
		def getBasicConfig():
			token = request.args.get('token')
			if token is None:
				self.logger("warn@Request for basic config received with no token.")
				return Response("Malformed request, token argument does not exist."), 400
			isAuthenticated = self.checkIfTokenValid(token)
			if isAuthenticated:
				success, values = self.getConfigFileValues()
				if success:
					self.logger("info@User " + token.split(':')[0] + " requested basic config." )
					returnedJSON = {'otherPort': int(values[0]), 'layout': values[1], 'map':values[2]}
					return Response(response=json.dumps(returnedJSON)), 200
				else:
					return Response("Failed to retrieve basic config."), 404
			else:
				self.logger("warn@User " + token.split(':')[0] + " attempted to request basic config file and was not authenticated.")
				return Response("User is not authenticated."), 401

		#Methode permettant de retrouver le nom des fichiers de configuration des données des fusées. 
		#Elle retourne 200 et la liste des fichiers de configuration des données des fusées, 400 si
		#le token n'a pas été fourni en argument, 401 si l'utilisateur n'est pas authentifié et 404
		#si le path vers les fichiers de configurations n'existe pas.
		@self.app.route("/config/rockets", methods=['GET'])
		def listRockets():
			token = request.args.get('token')
			#Si le token n'a pas été fourni en argument.
			if token is None:
				self.logger("warn@Request for rocket data description file names received no token.")
				return Response("Malformed request, token argument does not exist."), 400
			isAuthenticated = self.checkIfTokenValid(token)
			#Si l'utilisateur est authentifié.
			if isAuthenticated:
				self.logger("info@User " + token.split(':')[0] + " requested rocket data description file names.")
				#Verifier que le path vers les fichiers de configuration des fusées existe.
				if os.path.exists(self.pathToRocketsConfig):
					files = self.listFilesInDirectory(self.pathToRocketsConfig)
					dictionaryOfFiles = {}
					for i in range(0, len(files)):
						filename, file_extension = os.path.splitext(files[i])
						if file_extension == '.xml':
							dictionaryOfFiles['File' + str(i)] = files[i]
					self.logger("info@rocket data description file names was sent to user " + token) # ADDED Said
					return Response(response=json.dumps(dictionaryOfFiles)), 200
				else:
					 #Le path vers les fichiers de configuration des fusées n'existe pas.
					self.logger("error@Path " + self.pathToRocketsConfig + " does not exist.")
					return Response("Path " + self.pathToRocketsConfig + " does not exist."), 404
			else:
				#L'utilisateur n'est pas authentifié.
				self.logger("warn@User " + token.split(':')[0] + " attempted to request rockets data description file names and was not authenticated.")
				return Response("User is not authenticated."), 401

		#Methode permettant l'envoi d'un fichier de configuration des données de la fusée à 
		#l'utilisateur. Elle retourne 200 et le fichier en cas de succès, 400 si l'utilisateur
		#n'a pas fourni son token en argument, 401 si l'utilisateur n'est pas authentifié et 404
		#si le fichier demandé n'existe pas.
		@self.app.route("/config/rockets/<name>", methods=['GET'])
		def sendRocketFile(name):
			token = request.args.get('token')
			#Si le token n'a pas été fourni en argument
			if token is None:
				self.logger("warn@Request for rocket data description file received no token.")
				return Response("Malformed request, token argument does not exist."), 400
			isAuthenticated = self.checkIfTokenValid(token)
			#Si l'utilisateur est authentifié
			if isAuthenticated:
				self.logger("info@User " + token.split(':')[0] + " requested rocket data description file " + name + ".")
				#Si le fichier demandé existe
				if os.path.exists(os.path.join(self.pathToRocketsConfig, name)):
					filePath = '../' + os.path.join(self.pathToRocketsConfig, name)
					return send_file(filePath, mimetype='text/xml'), 200
				else:
					#Le fichier n'existe pas.
					return Response("File " + name + " does not exist."), 404
			#Si l'utilisateur n'est pas authentifié
			else:
				self.logger("warn@User " + token.split(':')[0] + " attempted to request rockets data description file and was not authenticated.", "WARNING")
				return Response("User is not authenticated."), 401

		#Methode permettant l'envoi d'un fichier de configuration des données de la fusée à 
		#l'utilisateur. Elle retourne 200 et le fichier en cas de succès, 400 si l'utilisateur
		#n'a pas fourni son token en argument, 401 si l'utilisateur n'est pas authentifié et 404
		#si le fichier demandé n'existe pas.
		@self.app.route("/config/miscFiles/<name>", methods=['GET'])
		def sendPDFFile(name):
			token = request.args.get('token')
			#Si le token n'a pas été fourni en argument
			if token is None:
				self.logger("warn@Request for misc file received no token.")
				return Response("Malformed request, token argument does not exist."), 400
			isAuthenticated = self.checkIfTokenValid(token)
			#Si l'utilisateur est authentifié
			if isAuthenticated:
				self.logger("info@User " + token.split(':')[0] + " requested misc file " + name + ".")
				#Si le fichier demandé existe
				if os.path.exists(os.path.join(self.pathToMiscFiles, name)):
					filePath = '../' + os.path.join(self.pathToMiscFiles, name)
					return send_file(filePath, mimetype='application/pdf'), 200
				else:
					#Le fichier n'existe pas.
					return Response("File " + name + " does not exist."), 404
			#Si l'utilisateur n'est pas authentifié
			else:
				self.logger("warn@User " + token.split(':')[0] + " attempted to request misc file name and was not authenticated.", "WARNING")
				return Response("User is not authenticated."), 401
			
		#Methode permettant de retrouver le nom des fichiers de configuration des données des fusées. 
		#Elle retourne 200 et la liste des fichiers de configuration des données des fusées, 400 si
		#le token n'a pas été fourni en argument, 401 si l'utilisateur n'est pas authentifié et 404
		#si le path vers les fichiers de configurations n'existe pas.
		@self.app.route("/config/miscFiles", methods=['GET'])
		def listMiscFiles():
			token = request.args.get('token')
			#Si le token n'a pas été fourni en argument.
			if token is None:
				self.logger("warn@Request for misc file names received no token.")
				return Response("Malformed request, token argument does not exist."), 400
			isAuthenticated = self.checkIfTokenValid(token)
			#Si l'utilisateur est authentifié.
			if isAuthenticated:
				self.logger("info@User " + token.split(':')[0] + " requested misc file names.")
				#Verifier que le path vers les fichiers de configuration des fusées existe.
				if os.path.exists(self.pathToMiscFiles):
					files = self.listFilesInDirectory(self.pathToMiscFiles)
					dictionaryOfFiles = {}
					for i in range(0, len(files)):
						filename, file_extension = os.path.splitext(files[i])
						if file_extension == '.pdf':
							dictionaryOfFiles['File' + str(i)] = files[i]
					self.logger("info@misc file names was sent to user " + token) # ADDED Said
					return Response(response=json.dumps(dictionaryOfFiles)), 200
				else:
					 #Le path vers les fichiers de configuration des fusées n'existe pas.
					self.logger("error@Path " + self.pathToMiscFiles + " does not exist.")
					return Response("Path " + self.pathToMiscFiles + " does not exist."), 404
			else:
				#L'utilisateur n'est pas authentifié.
				self.logger("warn@User " + token.split(':')[0] + " attempted to request misc file names and was not authenticated.")
				return Response("User is not authenticated."), 401

		#Methode permettant de récupérer la carte. Elle retourne 200 et la carte en cas de succès,
		#400 dans le cas où le token n'a pas été fourni en argument, 401 si l'utilisateur n'est pas authentifié
		#404 si le fichier de configuration contenant les inforamtions de la carte est inexistant.
		@self.app.route("/config/map", methods=['GET'])
		def getConfigMap():
			token = request.args.get('token')
			#Si le token n'a pas été fourni en argument
			if token is None:
				self.logger("warn@Request for map received with no token.")
				return Response("Malformed request, token argument does not exist."), 400
			isAuthenticated = self.checkIfTokenValid(token)
			#Si l'utilisatuer est authentifié
			if isAuthenticated:
				success, values = self.getConfigFileValues()
				#Si l'obtention des données du fichier de configuration s'est fait avec succès
				if success:
					self.logger("info@User " + token.split(':')[0] + " requested map." )
					returnedJSON = {'map':values[2]}
					return Response(response=json.dumps(returnedJSON)), 200
				else:
					#Le fichier de configuration contenant les données n'existe pas.
					return Response("Failed to retrieve map config."), 404
			else:
				#L'utilisateur n'est pas authentifié.
				self.logger("warn@User " + token.split(':')[0] + " attempted to request map and was not authenticated.")
				return Response("User is not authenticated."), 401
				
				
		if(os.path.exists(self.connectedUsersFileName)):
			os.remove(self.connectedUsersFileName)
		self.logger("info@REST Server started.")
		self.app.run(host='0.0.0.0', port=80,threaded=True)
		
		

	#Methode permettant de verifier si le token est valide ou non. 
	#Elle retourne True si le token est valide, False autrement.
	def checkIfTokenValid(self, token):
		#Verifier si le fichier contenant les utilisateurs connectés existe ou pas.
		if not os.path.exists(self.connectedUsersFileName):
			self.logger("error@File '"+ self.connectedUsersFileName + "' was not found.")
			return False
		if token is not None:
			username = token.split(':')[0]
			parser = ET.XMLParser(remove_blank_text=True)
			tree = ET.parse(self.connectedUsersFileName, parser)
			root = tree.getroot()
			user = root.find(username)
			if user is not None:
				userToken = user.find('token')
				if userToken is not None and userToken.text == token:
					return True
		return False

	#Methode permettant d'écrire une entrée dans le fichier des utilisateurs connectés.
	#Cette méthode ne retourne rien, mais elle reçoit en paramètre le noeud racine de l'arbre XML, le
	#nom d'utilisateur et le token.
	def createConnectedUserEntry(self, root, givenUsername, token):
		userEntry = ET.SubElement(root, givenUsername)
		tok = ET.SubElement(userEntry, 'token')
		tok.text = token
		tree = ET.ElementTree(root)
		tree.write(self.connectedUsersFileName, pretty_print=True, xml_declaration=True, encoding="utf-8")

	#Methode permettant de retrouver les fichiers de configuration des données de la fusée
	#dans le répertoire contenant les fichiers de configuration.
	def listFilesInDirectory(self, pathToFiles):
		files = [f for f in listdir(pathToFiles) if isfile(join(pathToFiles, f))]
		return files

	#Methode permettant l'encryption des mots de passe reçu en paramètre. Elle retourne
	#un hash sha512 du mot de passe salé 0xCAFE fois.
	def encryptPassword(self, chosenPassword):
		value = hashlib.pbkdf2_hmac('sha512', bytes(chosenPassword, encoding='utf-8'), b'I love my grandma', 51966)
		return binascii.hexlify(value)

	#Methode permettant de lire le fichier de configuration de base afin d'extraire
	#le port du serveur de donnée, le layout et la carte. Elle retourne
	#un boolean représentant le succès ou l'échec de la récupération de la configuration
	#et, dans le cas d'un succès, une liste contenant les valeurs de la configuration de base.
	def getConfigFileValues(self):
		#Si le fichier de configuration n'existe pas.
		if os.path.exists(self.configXml):
			parser = ET.XMLParser(remove_blank_text=True)
			tree = ET.parse(self.configXml, parser)
			root = tree.getroot()
			otherPort = root.find('otherPort').text
			layout = root.find('layout').text
			theMap = root.find('map').text
			return True, [otherPort, layout, theMap]
		else:
			#Le fichier de configuration de base n'existe pas.
			self.logger("error@File " + self.configXml + " does not exist")
			return False, None
			
	def logger(self, logMessage):
		self.DispayLogMessage.emit(logMessage)		
	
			

	
