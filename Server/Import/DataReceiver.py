#!/usr/bin/python3
import socket
import sys
import logging
import serial
import csv
import queue
import base64
import binascii
import struct
import time
import datetime
from lxml import etree as ET
from PyQt5 import QtCore
import xml.etree.ElementTree
from Import.CANSid import CANSid
from Import.CANSid import CANDataType
from Import.CANSid import CANMsgDataTypes
from Import.EnumClasses import ModuleType
from Import.CANMessage import CANMessage
from Import.CustomUpdate import CustomUpdate


# ----------------------------------------CLASS----------------------------------------------#
# Classe ReceiverThread dérivée de la classe QtCore.Thread
# Elle permet d'encapsuler les méthodes utilisées par le thread responsable de la réception
# de données en mode simulation et en mode serial. Ces données sont vérifiées, formatées selon
# les requis du fichier xml de configuration et placées dans une queue thread safe partagée 
# avec le thread responsable de la transmission de ces données aux clients connectés au serveur.
# -------------------------------------------------------------------------------------------#
class ReceiverThread(QtCore.QThread):
	
	DispayLogMessage = QtCore.pyqtSignal(str)
	# ------------------------------------Constructor----------------------------------------#
	# Constructeur de la classe ReceiverThread
	# Il reçoit en paramètres:
	# - La liste des connections par socket établies avec le processus parent
	# - La liste des informations en quadruplets des usagers connectés
	# - La file pour contenir les données reçues du fichier csv ou du port usb série
	#   importants dans la console et dans un fichier
	# - Le path du fichier xml de configuration de l'UI de l'application mobile
	# - Le booléen permettant de déterminer si le mode serial est choisi
	# - Le lecteur du port serial ou le fichier csv dépendemment du mode serial ou simulation
	# ---------------------------------------------------------------------------------------#
	def __init__(self, connections, connectedUsers, dataQueue, xmlFileName, serialRead, reader):
		QtCore.QThread.__init__(self)
		self.conList = connections
		self.conUsers = connectedUsers
		self.queue = dataQueue
		self.serialRead = serialRead
		self.reader = reader
		self.CAN_List = []
		self.GetxmlCanList(xmlFileName, self.CAN_List)

	# ----------------------------------------Method------------------------------------------#
	# Redéfinition de la méthode run() de la classe de base QtCore.Thread
	# Il s'agit de la méthode exécutée par le thread lors de son démarrage
	# Elle permet de récupérer les données lues à partir du port série usb en mode serial ou
	# du fichier csv en mode simulation et les stocker dans la file partagée avec le thread 
	# chargé d'envoyer les données aux clients connectés au serveur.
	# Elle permet aussi, en mode simulation, d'ouvrir le fichier csv, le parcourir ligne par
	# ligne, vérifier la validité des données et les formater avant de les stocker dans la file
	# En mode serial, elle permet de faire appel à une fonction qui s'occupe de la vérification
	# et du formatage des données.
	# Elle est éxécutée en boucle conditionnée par la non activation de l'événement stop_event
	# ----------------------------------------------------------------------------------------#
	def run(self):
		# Mode serial sélectionné
		if self.serialRead:
			# Ouvrir le port série usb
			self.reader.open()
			if self.reader.isOpen():
				while True:
					# Existance de clients connectés
					if self.conList and self.conUsers:
						# Lecture des données ligne par ligne
						dataBase64 = self.reader.readline()
						dataOutput = []
						# Le message est ignoré en cas de donnée invalide 
						if dataBase64.decode() == '':
							self.logger("warn@Message rejected because of invalid data: " + dataBase64.decode())
							continue
						if self.checkIfDataValid(dataBase64.decode(), dataOutput):
							self.queue.put(dataOutput[0].encode())						
			if self.reader.isOpen():
				# Fermer le port série usb
				self.reader.close()
		# Mode simulation sélectionné
		else:
			while True:
				try:					
					with open(self.reader, "r", encoding="ISO-8859-1") as csvFile:							
						refTime = 0.0				
						rowNumber = 0
						readCSV = csv.reader(csvFile, delimiter=';')						
						for row in readCSV:
							while not self.conList or not self.conUsers:
								time.sleep(1)
							msgID = ''
							destID = ''
							destSerial = 0
							srcID = ''
							srcSerial = 0
							data1 = 0
							data2 = 0
							messStatusPlot = ''
							messLogWidget = ''
												
							rowNumber += 1
							if rowNumber == 1:
								continue
							elif len(row) < 9:
								self.logger('warn@row ' + str(rowNumber) + ': Message ignored, missing data')
								continue
							elif len(row) > 9:
								self.logger('warn@row ' + str(rowNumber) + ': Message ignored, extra data')
								continue
							elif row[1] != 'IN':
								self.logger('warn@row ' + str(rowNumber) + ': Message ignored, Direction value is not IN')
								continue				
							else:
								isvalid = True
								for i in range(0, 8):
									if row[i] == '':
										self.logger('warn@row ' + str(rowNumber) + ': Message ignored, missing data')
										isvalid = False
										break
								if not isvalid:
									continue
								try :						
									msgIDstr = row[6]
									srcID = self.getModuleType(row[2])
									if srcID == ModuleType.UNKNOWN_MODULE:
										if type(row[2]) is not str:
											strSrcId = str(row[2])
										else:
											strSrcId = row[2]
										self.logger('warn@row ' + str(rowNumber) + ': Message ignored, srcID ' + strSrcId +' is UNKNOWN MODULE')
										continue
									srcSerial = int(row[3], 16)
									destID = self.getModuleType(row[4])													
									if row[5] == 'ALL_SERIAL_NBS':
										destSerial = 15
									else:
										destSerial = int(row[5], 16)
									messStatusPlot = msgIDstr + ';' + str(srcID).split('.')[1] + '(' + str(srcSerial) + ')' + ';' + str(destID).split('.')[1] + ';' + str(destSerial) + ';'						
									msgID = msgIDstr
									for i in range(7,9):
										try:
											dataType = str(CANMsgDataTypes[CANSid[msgIDstr]][i - 7]).split('.')[1]
											data = self.getDataValueFromString(row[i], dataType)
											data_str = ''
											if dataType == 'MAGIC':
												if binascii.crc32(msgIDstr.encode()) == int(row[i]):
													data_str = dataType + ';' + row[i]
												else:
													data_str = ''
													isvalid = False
													self.logger('warn@row ' + str(rowNumber) + ': Message ignored, CRC32 of msgID and MAGIC value does not match')
													break
											elif dataType == 'NONE':
												data_str = dataType + ';' + '0'
											else:
												data_str = dataType + ';' + row[i]
											messStatusPlot += data_str
											if i <= 7:
												data1 = data
												messStatusPlot += ';'										
											else:
												data2 = data									
										except:
											isvalid = False
											self.logger('warn@row ' + str(rowNumber) + ': Message ignored, invalid data')
											break
								except:
									self.logger('warn@row ' + str(rowNumber) + ': Message ignored, invalid data')
									continue
								if not isvalid:
									continue
																
								try:
									CANMsg = CANMessage(msgID, destID, destSerial, srcID, srcSerial, data1, data2)
									messOutput = self.getMessageFormatted(CANMsg, rowNumber)
								except:
									self.logger('warn@row ' + str(rowNumber) + ': Message ignored, CANMessage attribute is invalid')
									continue
									
								if messOutput != '':
									messOutput = messOutput[:-1]
									messOutput = str(len(messOutput.split(';'))) + ';' + messOutput
								else:
									messOutput = ' '
								messLogWidget = row[0] + ';' + row[1] + ';' + row[2] + ';' + row[3] + ';' + row[4] + ';' +\
								row[5] + ';' + row[6] + ';' + row[7] + ';' + row[8] + '\n'
								messOutput = messOutput + '@' + messStatusPlot + '@' + messLogWidget
								messOutput = str(len(messOutput.split(';'))) + ';' + messOutput
								self.queue.put(messOutput.encode())
							try:					
								if rowNumber > 2 and float(row[0]) > refTime:
									time.sleep(float(row[0]) - refTime)
								refTime = float(row[0])
							except:
								self.logger('warn@row ' + str(rowNumber) + ': Message ignored, invalid data')
								time.sleep(0.1)
								refTime += 0.1
				except FileNotFoundError:
					self.logger('error@FileNotFoundError: ' + self.reader + ' not found')
					sys.exit(1)
				except KeyboardInterrupt:
					self.logger("info@DataReceiver: Shutdown Request")
	
	# ----------------------------------------Method------------------------------------------#
	# getModuleType(): méthode appelée par la méthode run().
	# Elle prend en paramètres "moduleType", le type du module
	# Elle permet de retourner le type module au bon format
	# ----------------------------------------------------------------------------------------#	
	def getModuleType(self, moduleType):
		try:	
			if type(moduleType) is not ModuleType:
				if type(moduleType) is str:
					try:
						moduleType = ModuleType[moduleType]
					except:
						moduleType = ModuleType.UNKNOWN_MODULE
				else:
					moduleType = ModuleType(moduleType)	
		except:
			moduleType = ModuleType.UNKNOWN_MODULE
		return moduleType
	
	# ----------------------------------------Method------------------------------------------#
	# convertBase64ToInt(): méthode appelée par la méthode checkIfDataValid().
	# Elle prend en paramètres "dataBase64", la donnée brute reçue du port série
	# Elle permet de retourner la valeur numérique de la donnée en base hexadécimale
	# ----------------------------------------------------------------------------------------#
	def convertBase64ToInt(self, dataBase64):
		try:
			byteData = base64.b64decode(dataBase64)
			hexStrData = binascii.hexlify(byteData)	
			return int(hexStrData, 16)
		except:
			try:
				byteData = base64.b64decode(dataBase64)
				hexStrData = byteData.hex()	
				return int(hexStrData, 16)
			except:
				return 0
	
	# ----------------------------------------Method------------------------------------------#
	# checkIfDataValid(): méthode appelée par la méthode run().
	# Elle prend en paramètres "dataBase64", la donnée brute reçue du port série
	# et "dataOutput", la liste contenant le message formaté selon les requis
	# Elle permet de vérifier la validité de la donnée et la formatée selon le formatage requis
	# coté application
	# ----------------------------------------------------------------------------------------#
	def checkIfDataValid(self, dataBase64, dataOutput):
		dataHexValue = self.convertBase64ToInt(dataBase64)
		if dataHexValue == 0:
			self.logger("warn@Message rejected because of invalid data: " + dataBase64)
			return False
		reverseCRC32 = dataHexValue & 0xffffffff
		dataStrFormat = self.convertStrFormat(dataHexValue >> 32, 24)		
		dataControl = self.convertStrFormat(self.swapEndianness((dataHexValue >> 96) & 0xffffffff), 8)	
		data = int(dataControl, 16)
		
		# CANMessage attributes
		msgID = data & 0x7ff
		destID = (data >> 15) & 0x1f
		destSerial = (data >> 11) & 0xf
		srcID = (data >> 24) & 0x1f
		srcSerial = (data >> 20) & 0xf
		data1str = self.convertStrFormat(self.swapEndianness((dataHexValue >> 64) & 0xffffffff), 8)
		data2str = self.convertStrFormat(self.swapEndianness((dataHexValue >> 32) & 0xffffffff), 8)
		dataType1 = ''
		dataType2 = ''
		try:
			dataType1 = str(CANMsgDataTypes[CANSid(data & 0x7ff)][0]).split('.')[1]
			dataType2 = str(CANMsgDataTypes[CANSid(data & 0x7ff)][1]).split('.')[1]
		except:
			self.logger("warn@Message rejected because of invalid data type: " + dataBase64)
			return False
		data1 = self.getDataValueFromHex(data1str, dataType1)
		data2 = self.getDataValueFromHex(data2str, dataType2)
		CANMsg = CANMessage(msgID, destID, destSerial, srcID, srcSerial, data1, data2)
		messOutput = self.getMessageFormatted(CANMsg)
		if messOutput != '':
			messOutput = messOutput[:-1]
			messOutput = str(len(messOutput.split(';'))) + ';' + messOutput
		else:
			messOutput = ' '				
		#msgIDstr = str(CANSid(msgID)).split('.')[1]
		msgIDstr = ''
		try:
			msgIDstr = str(CANSid(msgID).name)
		except:
			self.logger("warn@Message rejected because of invalid CANSid: " + dataBase64)
			return False
		try:
			destType = str(ModuleType(destID).name)
		except:
			destType = str(ModuleType(0x1E).name)
		destSerialStr = str(destSerial)
		try:	
			srcType = str(ModuleType(srcID).name)
		except:
			srcType = str(ModuleType(0x1E).name)
		srcSerial = str(srcSerial)
		
		data1_str = self.getDataFormatted(data1, dataType1, msgIDstr)		
		data2_str = self.getDataFormatted(data2, dataType2, msgIDstr)
		
		messStatusPlot = ''
		if data1_str != '' and data1_str != '':
			messStatusPlot = msgIDstr + ';' + srcType + '(' + srcSerial + ')' + ';' + destType + ';' + destSerialStr + \
			';' + data1_str + ';' + data2_str
		if messStatusPlot != '':
			if destSerial == 15:
				destSerialStr = 'ALL_SERIAL_NBS'
			messLogWidget = str(0.0) + ';IN;' + srcType + ';' + srcSerial + ';' + destType + ';' + destSerialStr + \
			';' + msgIDstr + ';' + str(data1) + ';' + str(data2) + '\n'
			messOutput = messOutput + '@' + messStatusPlot + '@' + messLogWidget
			messOutput = str(len(messOutput.split(';'))) + ';' + messOutput
		else:
			messOutput = ''
			self.logger("warn@Message rejected because of invalid data: " + dataBase64)
			return False
		dataOutput.append(messOutput)
		givenCRC32 = self.swapEndianness(reverseCRC32)
		try:
			dataCRC32 = binascii.crc32(binascii.a2b_hex(dataStrFormat))
		except:
			self.logger("warn@Message rejected because of invalid data: " + dataBase64)
			return False
		if dataCRC32 != givenCRC32: 
			self.logger("warn@Message rejected because of CRC32: " + dataBase64)
		elif destType == ModuleType(0x1E).name:
			self.logger("warn@Message rejected because of destType is UNKNOWN_MODULE : " + dataBase64)	
		return dataCRC32 == givenCRC32 and destType != ModuleType(0x1E).name
		
	# ----------------------------------------Method------------------------------------------#
	# swapEndianness(): méthode appelée par la méthode convertStrFormat().
	# Elle prend en paramètres "data", la valeur de la donnée en format hexadécimale
	# Elle permet de retourner d'inverser l'endianesse de la donnée passée en paramètre
	# ----------------------------------------------------------------------------------------#
	def swapEndianness(self, data):
		return data >> 24 | (data & 0xff0000) >> 8 | (data & 0xff00) << 8 | (data & 0xff) << 24
	
	# ----------------------------------------Method------------------------------------------#
	# convertStrFormat(): méthode appelée par la méthode checkIfDataValid().
	# Elle prend en paramètres "data", la valeur de la donnée en format hexadécimale
	# et "byteCount", nombre d'octets ocupés par la donnée
	# Elle permet de retourner la donnée en format hexadécimal
	# ----------------------------------------------------------------------------------------#	
	def convertStrFormat(self, data, byteCount):
		dataStrFormat = format(data, 'x')
		longStr = len(dataStrFormat)
		if longStr < byteCount:
			for i in range(0,byteCount-longStr):
				dataStrFormat = '0' + dataStrFormat
		return dataStrFormat
	# ----------------------------------------Method------------------------------------------#
	# getDataValueFromHex(): méthode appelée par la méthode checkIfDataValid().
	# Elle prend en paramètres "hexData", la valeur hexadécimale de la donnée
	# et "dataType", le type de la donnée
	# Elle permet de retourner la valeur de la donnée en format décimal 
	# ----------------------------------------------------------------------------------------#		
	def getDataValueFromHex(self, hexData, dataType):
		if dataType == 'FLOAT':
			retValue = struct.unpack('!f', bytes.fromhex(hexData))[0]
			if retValue < 0.0001:
				retValue = 0.0
			return retValue
		elif dataType == 'INT':
			dataOutput = int(hexData, 16)
			if dataOutput > 0x7FFFFFFF:
				dataOutput -= 0x100000000
			return dataOutput
		else:
			return int(hexData, 16) & 0xFFFFFFFF
	
	# ----------------------------------------Method------------------------------------------#
	# getDataValueFromString(): méthode appelée par la méthode checkIfDataValid().
	# Elle prend en paramètres "strData", la forme hexadécimale de la donnée
	# et "dataType", le type de la donnée
	# Elle permet de retourner la valeur de la donnée en format décimal 
	# ----------------------------------------------------------------------------------------#		
	def getDataValueFromString(self, strData, dataType):
		if dataType == 'FLOAT':
			return float(strData)
		elif dataType == 'INT':
			return int(strData)
		else:
			return int(strData) & 0xFFFFFFFF
			
	
	# ----------------------------------------Method------------------------------------------#
	# getDataFormatted(): méthode appelée par la méthode checkIfDataValid().
	# Elle prend en paramètres "data", la valeur de la donnée, "dataTypeStr", le type de la donnée
	# et "msgIdStr", l'identifiant du message en format chaine de caractères
	# Elle permet de retourner la donnée formatée selon le format '"type" "valeur"'  
	# ----------------------------------------------------------------------------------------#	
	def getDataFormatted(self, data, dataTypeStr, msgIdStr):
		dataOutput = ''
		try:
			if dataTypeStr == 'INT' or dataTypeStr == 'FLOAT' or dataTypeStr == 'UNSIGNED' or dataTypeStr == 'TIMESTAMP':
				dataOutput = dataTypeStr + ';' + str(data)
			elif dataTypeStr == 'MAGIC':
				if binascii.crc32(binascii.a2b_hex(msgIdStr)) == data:
					dataOutput = dataTypeStr + ';' + str(data)
				else:
					dataOutput = ''	
			elif dataTypeStr == 'NONE':
				dataOutput = dataTypeStr + ';' + '0'
			elif dataTypeStr == 'UNKNOWN':
				dataOutput = ''
			else:
				dataOutput = ''
		except:
			dataOutput = ''
		return dataOutput
		
	
	# ----------------------------------------Method------------------------------------------#
	# getMessageFormatted(): méthode appelée par les méthodes run() en mode simulation et par
	# la méthode checkIfDataValid() en mode serial
	# Elle prend en paramètres un objet de la classe CANMessage contenant le message à formater
	# et un 2ème paramètre optionel correspond au numéro de ligne du fichier csv utilisé 
	# uniquement en mode simulation pour débogage
	# Elle permet de parcourir les CAN de la liste initialisée à partir du fichier xml, identifier
	# identifier les Ids qui correspondent à l'Id du CANMsg passé en paramètre et formater le
	# message selon les attributs de la CAN correspondante. Le message est dupliqué en cas ou
	# plusieurs CAN détiennent le même Id que le CANMsg
	# ----------------------------------------------------------------------------------------#	
	def getMessageFormatted(self, CANMsg, rowNumber = 0):
		messOutput = ''	
		if not self.serialRead:
			logMessage = 'row ' + str(rowNumber) + ': '
		else:
			logMessage = ''		
		try:
			for can in self.CAN_List:
				dataDisplay = "DATA1"
				dataUnit = ''
				minAcceptable = ''
				maxAcceptable = ''
				chiffresSign = ''
				customUpdate = ''
				customUpdateParam = ''
				customAcceptable = ''
				updateEach = ''
				colorOfData = 'GREEN'
				dataToDisplay = CANMsg.data1
				displayData = 'data1'
				dataType = CANMsgDataTypes[CANSid(CANMsg.msgID)][0] 
				formattedData = ''
				dataIsValid = True
				if 'id' in can.keys() and 'name' in can.keys() and can.get('id') is not None and can.get('id') is not None and\
				str(can.get('id')) == str(CANMsg.msgID).split('.')[1]:
					for attribKey in can.keys():
						if attribKey == 'display' and can.get('display') is not None:
							dataDisplay = can.get('display')[2:][:5]
							if can.get('display').find(' ') != -1:
								dataUnit = ' ' + can.get('display').split(' ')[1]
						elif attribKey == 'minAcceptable' and can.get('minAcceptable') is not None:
							minAcceptable = can.get('minAcceptable')
						elif attribKey == 'maxAcceptable' and can.get('maxAcceptable') is not None:
							maxAcceptable = can.get('maxAcceptable')
						elif attribKey == 'chiffresSign' and can.get('chiffresSign') is not None:
							chiffresSign = can.get('chiffresSign')
						elif attribKey == 'customUpdate' and can.get('customUpdate') is not None:
							customUpdate = can.get('customUpdate')
						elif attribKey == 'customUpdateParam' and can.get('customUpdateParam') is not None:
							customUpdateParam = can.get('customUpdateParam')
						elif attribKey == 'customAcceptable' and can.get('customAcceptable') is not None:
							customAcceptable = can.get('customAcceptable')
						elif attribKey == 'updateEach' and can.get('updateEach') is not None:
							updateEach = can.get('updateEach')
						elif attribKey == 'specificSource' and can.get('specificSource') is not None:
							if str(ModuleType(CANMsg.srcID).name) != can.get('specificSource'):
								dataIsValid = False
								logMessage += 'Message ignored for UI_Id <' + can.get('name') + '.' + can.get('id') + '>' + ': Input data (' + \
								str(ModuleType(CANMsg.srcID).name) + ') and specificSource (' + can.get('specificSource') + ') does not match'
								#self.logger('warn@' + logMessage)
						elif attribKey == 'serialNb' and can.get('serialNb') is not None:
							if str(CANMsg.srcSerial) != can.get('serialNb'):
								dataIsValid = False
								logMessage += 'Message ignored for UI_Id <' + can.get('name') + '.' + can.get('id') + '>' + ': Input data (' + \
								str(CANMsg.srcSerial) + ') and serialNb (' + can.get('serialNb') + ') does not match'
								#self.logger('warn@' + logMessage)					
					if dataDisplay == "DATA2":
						dataToDisplay = CANMsg.data2
						displayData = 'data2'
						dataType = CANMsgDataTypes[CANSid(CANMsg.msgID)][1]
					if minAcceptable != '' and dataType == 'FLOAT':
						minAcceptable = float(minAcceptable)
						if dataToDisplay < minAcceptable:
							colorOfData = 'RED'
					elif minAcceptable != '' and dataType == 'INT':
						minAcceptable = int(minAcceptable)
						if minAcceptable > 0x7FFFFFFF:
							minAcceptable -= 0x100000000
						if dataToDisplay < minAcceptable:
							colorOfData = 'RED'
					elif minAcceptable != '':
						minAcceptable = int(minAcceptable)
						if dataToDisplay < minAcceptable:
							colorOfData = 'RED'
					if maxAcceptable != '' and dataType == 'FLOAT':
						maxAcceptable = float(maxAcceptable)
						if dataToDisplay > maxAcceptable:
							colorOfData = 'RED'
					elif maxAcceptable != '' and dataType == 'INT':
						maxAcceptable = int(maxAcceptable)
						if maxAcceptable > 0x7FFFFFFF:
							maxAcceptable -= 0x100000000
						if dataToDisplay > maxAcceptable:
							colorOfData = 'RED'
					elif maxAcceptable != '':
						maxAcceptable = int(maxAcceptable, 16)
						if dataToDisplay > maxAcceptable:
							colorOfData = 'RED'
					if chiffresSign != '':
						chiffresSign = '.' + chiffresSign + 'f'
						dataToDisplay = format(dataToDisplay, chiffresSign)
					if customUpdate != '':
						custUpFuncToCall = getattr(CustomUpdate, customUpdate)
						formattedData = custUpFuncToCall(CANMsg, customUpdateParam)
						if type(formattedData) is not str:
							formattedData = str(formattedData)
					if customAcceptable != '':
						custUpFuncToCall = getattr(CustomUpdate, customAcceptable)
						if not custUpFuncToCall(CANMsg):
							colorOfData = 'RED'
					if formattedData != '':
						messOutput += can.get('id') + ';' + formattedData + ';' + colorOfData + ';'
					else:
						messOutput += can.get('id') + ';' + str(dataToDisplay) + dataUnit + ';' + colorOfData + ';'
						
					if dataIsValid and formattedData != 'None':
						messOutput += 'ok;'
					else:
						messOutput += 'no;'
					if formattedData == 'None':
						logMessage = 'Message ignored for UI_Id <' + can.get('name') + '.' + can.get('id') + '>' + \
							': CustomUpdate function returns <None> value'
						#self.logger('warn@' + logMessage)							
		except:
			messOutput = ''					
		return messOutput
		
	
	# ----------------------------------------Method------------------------------------------#
	# getxmlCanList(): méthode appelée dans le constructeur pour initialiser la liste des CAN
	# correspondants au DataDisplayer
	# Elle prend en paramètres le path du fichier xml de configuration de l'UI de l'application
	# mobile et la liste des CAN pour contenir les CAN du fichier xml
	# Elle permet de parcourir le fichier xml, identifier le tag DataDisplayer et ajouter les 
	# tag CAN correspondantes à la liste passée en paramètre
	# ----------------------------------------------------------------------------------------#	
	def GetxmlCanList(self, xmlFileName, CAN_List):
		xmlParser = ET.parse(xmlFileName, ET.XMLParser(remove_blank_text=True)).getroot()			
		for dataDisplayer in xmlParser.iter(tag='DataDisplayer'):
			for can in dataDisplayer.iter(tag='CAN'):				
				CAN_List.append(can)
		
	
	# ----------------------------------------Method------------------------------------------#
	# logger(): méthode appelée par les méthodes de la classe pour afficher un événement
	# Elle prend en paramètres "sMessage", une chaîne de caractères
	# Elle permet d'envoyer le message (en paramèetre) à l'interface graphique pour l'afficher
	# dans l'éditeur de texte dédié journal du serveur
	# ----------------------------------------------------------------------------------------#
	def logger(self, logMessage):
		self.DispayLogMessage.emit(logMessage)
