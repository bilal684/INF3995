#!/usr/bin/python3

from PyQt5 import QtCore
import time
import datetime


# ----------------------------------------CLASS----------------------------------------------#
# Classe ConnectedUsersThread dérivée de la classe QtCore.Thread
# Elle permet d'encapsuler les méthodes utilisées par le thread chargé de la transmission
# des informations, concernant les usagers connectés
# -------------------------------------------------------------------------------------------#
class ConnectedUsersThread(QtCore.QThread):
	
	DisplayConnectedUsers = QtCore.pyqtSignal(str)
	# ------------------------------------Constructor----------------------------------------#
	# Constructeur de la classe ConnectedUsersThread
	# Il reçoit en paramètres:
	# - La liste des informations en quadruplets des usagers connectés
	# ---------------------------------------------------------------------------------------#
	def __init__(self, connectedUsers): 
		QtCore.QThread.__init__(self)
		self.connectedUsers = connectedUsers
	
	# ----------------------------------------Method------------------------------------------#
	# Redéfinition de la méthode run() de la classe de base QtCore.Thread
	# Il s'agit de la méthode exécutée par le thread lors de son démarrage
	# Elle permet de récupérer les données de la liste connectedUsers et les envoyer 
	# par socket au processus chargé de les afficher dans une console séparée
	# Le protocole utilisé est "Stop and Wait" pour assurer la bonne réception de données
	# côté client
	# ----------------------------------------------------------------------------------------#
	def run(self):
		clearConnUsersConsole = False		
		while True:			
			message = ''
			for conn in self.connectedUsers:					
				message += conn[0] + ';' + conn[1] + ';' + conn[2][1:] + ';' + str(datetime.datetime.now() - conn[3]) + '@'
				if not clearConnUsersConsole:
					clearConnUsersConsole = True
			if message != '':
				message = message[:-1]
				self.displayMessage(message)
				time.sleep(0.1)
			elif clearConnUsersConsole:
				self.displayMessage('clear console')
				clearConnUsersConsole = False
	
	# ----------------------------------------Method------------------------------------------#
	# displayMessage(): méthode appelée par la méthode run().
	# Elle prend en paramètres "sMessage", une chaîne de caractères
	# Elle permet d'envoyer le message (en paramèetre) à l'interface graphique pour l'afficher
	# dans l'éditeur de texte dédié à l'affichage des utilisateurs connectés
	# ----------------------------------------------------------------------------------------#		
	def displayMessage(self, sMessage):
		self.DisplayConnectedUsers.emit(sMessage)
