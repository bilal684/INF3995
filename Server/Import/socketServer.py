#!/usr/bin/python3
import socket
import os
import platform
import threading
import sys, getopt
import logging
import serial
import netifaces
import signal
import queue
import time
import datetime
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from lxml import etree as ET
from Import.EnumClasses import MapName



# ----------------------------------------CLASS----------------------------------------------#
# Classe SocketThread dérivée de la classe QtCore.Thread
# Elle permet d'encapsuler les méthodes utilisées par le thread chargé de vérifier les jetons
# présentés par les clients voulant se connecter au serveur et d'établir des connexions avec eux
# -------------------------------------------------------------------------------------------#
class SocketThread(QtCore.QThread):
	DispayLogMessage = QtCore.pyqtSignal(str)
	
	# ------------------------------------Constructor----------------------------------------#
	# Constructeur de la classe ReceiverThread
	# Il reçoit en paramètres:
	# - L'adresse IP du serveur à utiliser pour la création du socket
	# - La liste des connections par socket établies avec le processus parent
	# - La liste des adresses clients connectés au serveur
	# - Le numéro de port à utiliser pour la création du socket
	# ---------------------------------------------------------------------------------------#
	def __init__(self, host, connections, clientAddresses, portNumber):
		QtCore.QThread.__init__(self)
		self.portNumber = portNumber
		self.conList = connections
		self.clAddr = clientAddresses
		self.host = host
		self.connectedUsersFileName = "./Account/connectedUsers.xml"
		self.TIMEOUT = 2.0 # timeout for socket
	
	
	# ----------------------------------------Method------------------------------------------#
	# Redéfinition de la méthode run() de la classe de base QtCore.Thread
	# Il s'agit de la méthode exécutée par le thread lors de son démarrage
	# Elle permet de récupérer les données de créer un socket et se mettre à la réception 
	# des proposition des connexions de la part des clients voulant se connecter au serveur
	# Elle vérifie la validité du jeton envoyé par le client, établi la connexion avec ce client
	# et ajoute cette connexion à la liste des connexions avec le serveur
	# ----------------------------------------------------------------------------------------#
	def run(self):
		mySocket = socket.socket()
		mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			mySocket.bind((self.host,int(self.portNumber)))
		except OSError:
			self.logger("error@The port number " + str(self.portNumber) + "is already in use")
			sys.exit(2)
		
		mySocket.listen(1)
		self.logger("info@Server is listening ...")
		while True: 
			try:
				connection, cAddress = mySocket.accept()
				token = connection.recv(1024)
				if cAddress not in self.clAddr  and self.checkIfTokenValid(token.decode(), self.connectedUsersFileName):
					self.logger("info@Connection established with: " +\
					str(cAddress[0]) + ':' + str(cAddress[1]))
					connection.settimeout(self.TIMEOUT)
					self.conList.append(connection)
					self.clAddr.append(cAddress)		
				else:
					connection.send("Connection unauthorized!".encode())
					# Clean up the connection
					connection.close()
					self.logger("warn@Connection unauthorized with " +\
					str(cAddress[0]) + ':' + str(cAddress[1]))
			except KeyboardInterrupt:
				self.logger("info@KeyboardInterrupt: Shutdown Request")
				break
			except socket.error as e:
				self.logger('error@' + str(e) + ": Shutdown Request")
				break
		mySocket.close()
		
	
	# ----------------------------------------Method------------------------------------------#
	# checkIfTokenValid(): méthode appelée par la méthode run().
	# Elle prend en paramètres "token", jeton envoyé par le client voulant se connecter au serveur
	# et "fileName", le chemin du fichier xml contenant les jetons valides 
	# Elle permet de vérifier la validité du jeton passé en paramètre et retourn vrai lorsque valide
	# ou faux sinon
	# ----------------------------------------------------------------------------------------#	
	def checkIfTokenValid(self, token, fileName):
		if not os.path.exists(fileName):
			return False
		if token is not None:
			username = token.split(':')[0]
			parser = ET.XMLParser(remove_blank_text=True)
			tree = ET.parse(fileName, parser)
			root = tree.getroot()
			user = root.find(username)
			if user is not None:
				userToken = user.find('token')
				if userToken is not None and userToken.text == token:
					return True
		return False
		
	
	# ----------------------------------------Method------------------------------------------#
	# displayMessage(): méthode appelée par la méthode run().
	# Elle prend en paramètres "sMessage", une chaîne de caractères
	# Elle permet d'envoyer le message (en paramèetre) à l'interface graphique pour l'afficher
	# dans l'éditeur de texte dédié à l'affichage des utilisateurs connectés
	# ----------------------------------------------------------------------------------------#		
	def logger(self, logMessage):
		self.DispayLogMessage.emit(logMessage)
