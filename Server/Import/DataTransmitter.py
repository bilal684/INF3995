#!/usr/bin/python3
import socket
import logging
from PyQt5 import QtCore
import queue
import time


# ----------------------------------------CLASS----------------------------------------------#
# Classe TransmitterThread dérivée de la classe QtCore.Thread
# Elle permet d'encapsuler les méthodes utilisées par le thread responsable de la transmission
# de données vers les clients par socket. Ces données sont récupérées à partir d'une queue
# thread safe partagée avec le thread responsable de la réception de données.
# -------------------------------------------------------------------------------------------#
class TransmitterThread(QtCore.QThread):
	
	DispayLogMessage = QtCore.pyqtSignal(str)
	# ------------------------------------Constructor----------------------------------------#
	# Constructeur de la classe TransmitterThread
	# Il reçoit en paramètres:
	# - La liste des connections par socket établies avec le processus parent
	# - La liste des informations en quadruplets des usagers connectés
	# - La liste des adresses clients connectés au serveur
	# - La file des données reçues du fichier csv ou du port usb série
	# ---------------------------------------------------------------------------------------#
	def __init__(self, connections, connectedUsers, clientAddresses, dataQueue): 
		QtCore.QThread.__init__(self)
		self.conList = connections
		self.conUsers = connectedUsers
		self.clAddrList = clientAddresses
		self.queue = dataQueue
	
	# ----------------------------------------Method------------------------------------------#
	# Redéfinition de la méthode run() de la classe de base QtCore.Thread
	# Il s'agit de la méthode exécutée par le thread lors de son démarrage
	# Elle permet de récupérer les données de la file des données et les envoyer 
	# par socket aux clients inclus dans la liste des clients connectés au serveur
	# Elle permet aussi de détecter la fermeture d'une socket client pour la retirer de 
	# la liste et stopper l'envoie de données à ce client.
	# Le protocole utilisé est "Stop and Wait" pour assurer la bonne réception de données
	# côté client
	# Elle est éxécutée en boucle conditionnée par la non activation de l'événement stop_event
	# ----------------------------------------------------------------------------------------#
	def run(self):
		while True:
			if not self.queue.empty() and self.conList:
				data = self.queue.get()
				#self.logger('debug@' + data.decode())
				for conn in self.conList:
					if any(str(self.clAddrList[self.conList.index(conn)][0]) in conUser for conUser in self.conUsers):
						try:
							conn.sendall(data)
							while conn.recv(1024).decode().lower() != 'ok':
								conn.sendall(data)
						except:
							if not self.conUsers:
								self.logger("info@Server is listening ...")
					else:
						self.logger("warn@Connection is interrupted with " +\
						str(self.clAddrList[self.conList.index(conn)][0]) + ':' +\
						str(self.clAddrList[self.conList.index(conn)][1]))				
						del self.clAddrList[self.conList.index(conn)]
						self.conList.remove(conn)
						conn.close()
						if not self.conUsers:
							self.logger("info@Server is listening ...")
	
	
	# ----------------------------------------Method------------------------------------------#
	# logger(): méthode appelée par les méthodes de la classe pour afficher un événement
	# Elle prend en paramètres "sMessage", une chaîne de caractères
	# Elle permet d'envoyer le message (en paramèetre) à l'interface graphique pour l'afficher
	# dans l'éditeur de texte dédié journal du serveur
	# ----------------------------------------------------------------------------------------#
	def logger(self, logMessage):
		self.DispayLogMessage.emit(logMessage)
		
