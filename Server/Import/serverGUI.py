import sys
import os
import serial
import csv
import logging
import time
import queue
import datetime
from lxml import etree as ET
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi
from Import.EnumClasses import MapName
from Import.restServer import RestServer
from Import.DataReceiver import ReceiverThread
from Import.DataTransmitter import TransmitterThread
from Import.socketServer import SocketThread
from Import.ConnectedUsers import ConnectedUsersThread

# ----------------------------------------CLASS----------------------------------------------#
# Classe QTextEditLogger dérivée de la classe logging.Handler
# Elle permet d'offrir la possibilité de créer des logger à affichage dans un éditeur de texte
# -------------------------------------------------------------------------------------------#
class QTextEditLogger(logging.Handler):
    def __init__(self, parent, name, container):
        super().__init__()
        self.widget = QtWidgets.QTextEdit(parent)
        self.widget.setReadOnly(True)
        self.widget.setStyleSheet("background-color: lightGray")
        self.widget.setObjectName(name)
        container.addWidget(self.widget)

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)
  
# ----------------------------------------CLASS----------------------------------------------#
# Classe ServerGUI dérivée de la classe QtWidgets.QMainWindow
# Elle permet d'encapsuler les méthodes utilisées par le processus principal afin de créer
# l'interface graphique, gérer les événement récupérés 
# et créer les threads responsables des différentes fonctionalités du serveur
# -------------------------------------------------------------------------------------------#
class ServerGUI(QtWidgets.QMainWindow):
    def __init__(self, argumentsList, csvPath, rocketPath, logPath, configPath, configFile):
        super(self.__class__, self).__init__()
        #super(ServerGUI, self).__init__()
        loadUi('./Import/mainwindow.ui', self)
        self.setWindowTitle('Oronos PCB data analysis Server')
        self.move(0,0)
        self.DisplayLog = QTextEditLogger(self.verticalLayoutWidget_5, "DisplayLog", self.verticalLayout_9)
        #self.DisplayLog = QtWidgets.QTextEdit(self.verticalLayoutWidget_5)
        #self.DisplayLog.setObjectName("DisplayLog")
        #self.verticalLayout_9.addWidget(self.DisplayLog)
        self.csvPath = csvPath
        self.rocketPath = rocketPath
        self.configPath = configPath
        self.configFile = configFile
        self.m_sDefaultBaudrate = argumentsList[0]
        self.logger = self.GetLogger(logPath)
        self.InitializeGUI(argumentsList)
        self.Start.clicked.connect(self.On_Start_Clicked)
        self.Set_default.clicked.connect(self.On_Default_Clicked)
        self.Quit.clicked.connect(self.On_Quit_Clicked)
        self.csvFile.currentTextChanged.connect(self.On_CsvFile_CurrentTextChanged)
        self.serialPort.currentTextChanged.connect(self.On_SerialPort_currentTextChanged)
        self.rocket.currentTextChanged.connect(self.On_Rocket_CurrentTextChanged)
        self.map.currentTextChanged.connect(self.On_Map_CurrentTextChanged)
        self.simulation.clicked.connect(self.On_Simulation_Clicked)
        self.serial.clicked.connect(self.On_Serial_Clicked)
        self.portNumber.editingFinished.connect(self.On_PortNumber_EditingFinished)   
        self.baudrate.editingFinished.connect(self.On_Baudrate_EditingFinished)
        self.ThreadsAreCreated = False
        
    # ----------------------------------------Method------------------------------------------#
	# On_Start_Clicked(): méthode (slot) appelée lors de la réception de l'événement "click" du.
	# bouton "START"
	# ----------------------------------------------------------------------------------------#	
    @pyqtSlot()
    def On_Start_Clicked(self):
        self.Start.setEnabled(False)
        self.Set_default.setEnabled(False)
        self.csvFile.setEnabled(False)
        self.serialPort.setEnabled(False)
        self.rocket.setEnabled(False)
        self.map.setEnabled(False)
        self.serial.setEnabled(False)
        self.simulation.setEnabled(False)
        self.baudrate.setEnabled(False)
        self.portNumber.setEnabled(False)
        self.UpdateParameters()        
        
        self.Start.setStyleSheet("background-color: lightGray")
        try:
            self.CreateXmlConfig(self.configPath, self.configFile, self.m_sPortNumber, self.m_sRocketFileName, self.m_sMapName)
        except:
            self.logger.error("Failed to create xml config file")
            sys.exit(2)
            
        connections = []
        clientAddresses = []
        dataQueue = queue.Queue()
        connectedUsers = []
        host = self.IpServerAddress.text()
        xmlFilePath = os.path.join(self.rocketPath, self.m_sRocketFileName)
        
        self.sockThread = SocketThread(host, connections, clientAddresses, self.m_sPortNumber)
        self.sockThread.DispayLogMessage.connect(self.DispayLogMessage)
        self.sockThread.start()
        
        self.restServerThread = RestServer(host, connectedUsers)
        self.restServerThread.DispayLogMessage.connect(self.DispayLogMessage)
        self.restServerThread.start()
        
        self.receivThread = ReceiverThread(connections, connectedUsers, dataQueue, xmlFilePath, self.serial.isChecked(), self.GetReader())
        self.receivThread.DispayLogMessage.connect(self.DispayLogMessage)
        self.receivThread.start()
        
        self.transThread = TransmitterThread(connections, connectedUsers, clientAddresses, dataQueue)
        self.transThread.DispayLogMessage.connect(self.DispayLogMessage)
        self.transThread.start()
        
        self.connUsersThread = ConnectedUsersThread(connectedUsers)
        self.connUsersThread.DisplayConnectedUsers.connect(self.DisplayConnectedUsers)
        self.connUsersThread.start()
        
        self.ThreadsAreCreated = True
        
    # ----------------------------------------Method------------------------------------------#
	# On_Start_Clicked(): méthode (slot) appelée lors de la réception de l'événement "click" du.
	# bouton "Set_Default"
	# ----------------------------------------------------------------------------------------#	    
    @pyqtSlot()
    def On_Default_Clicked(self):        
        self.csvFile.setCurrentText(self.m_sDefaultCsvFileName)
        self.rocket.setCurrentText(self.m_sDefaultRocketFileName)
        self.map.setCurrentText(self.m_sDefaultMapName)
        self.baudrate.setText(self.m_sDefaultBaudrate)
        self.portNumber.setText(self.m_sDefaultPortNumber)
        self.serialPort.setCurrentText(self.m_sDefaultSerialPortPath)
        self.m_sConnectorType = self.m_sDefaultConnectorType
        self.UpdateParameters()
        if self.m_sDefaultConnectorType == 'simulation':     
            self.simulation.setChecked(True)
            self.csvFile.setEnabled(True)
            self.serial.setChecked(False)
            self.serialPort.setEnabled(False)
            self.baudrate.setEnabled(False)
        else:
            self.serial.setChecked(True)
            self.simulation.setChecked(False)           
            self.serialPort.setEnabled(True)
            self.baudrate.setEnabled(True)
            self.csvFile.setEnabled(False)
        self.logger.info("Default values ​​were chosen")
        
    # ----------------------------------------Method------------------------------------------#
	# On_Start_Clicked(): méthode (slot) appelée lors de la réception de l'événement "click" du.
	# bouton "QUIT"
	# ----------------------------------------------------------------------------------------#	
    @pyqtSlot()
    def On_Quit_Clicked(self):
        self.logger.info("Server is shutting down...")        
        #if self.ThreadsAreCreated:
            #self.sockThread.stop()
            #self.transThread.stop()
            #self.receivThread.stop()            
            #self.connUsersThread.stop()
            #self.restServerThread.stop()          
        time.sleep(1)
        #sys.exit(0)
        self.close()
        
    # ----------------------------------------Method------------------------------------------#
	# On_Start_Clicked(): méthode (slot) appelée lors de la réception de l'événement "click" du.
	# bouton "Simulation"
	# ----------------------------------------------------------------------------------------#	    
    @pyqtSlot()
    def On_Simulation_Clicked(self):
        self.UpdateParameters()
        if self.simulation.isChecked():
            self.simulation.setChecked(True)
            self.serial.setChecked(False)
            self.m_sConnectorType = "simulation"
            self.serialPort.setEnabled(False)
            self.baudrate.setEnabled(False)
            self.csvFile.setEnabled(True)
        else:
            self.simulation.setChecked(True)  
        self.SetCsvFileNameList()
        self.SetSerialPortPathList()
        self.SetRocketFileNameList()
        self.SetMapNameList()
    
    # ----------------------------------------Method------------------------------------------#
	# On_Start_Clicked(): méthode (slot) appelée lors de la réception de l'événement "click" du.
	# bouton "Serial"
	# ----------------------------------------------------------------------------------------#	    
    @pyqtSlot()
    def On_Serial_Clicked(self):
        self.UpdateParameters()
        if self.serial.isChecked():
            self.serial.setChecked(True)
            self.simulation.setChecked(False)
            self.m_sConnectorType = "serial"      
            self.serialPort.setEnabled(True)
            self.baudrate.setEnabled(True)
            self.csvFile.setEnabled(False)
        else:
            self.serial.setChecked(True)
        self.SetCsvFileNameList()
        self.SetSerialPortPathList()
        self.SetRocketFileNameList()
        self.SetMapNameList()
            
        
        
    @pyqtSlot()
    def On_CsvFile_CurrentTextChanged(self):
        pass
        
        
    @pyqtSlot()
    def On_Rocket_CurrentTextChanged(self):
        pass
        
        
    @pyqtSlot()
    def On_Map_CurrentTextChanged(self):
        pass
        
        
    @pyqtSlot()
    def On_SerialPort_currentTextChanged(self):
        pass
            
    # ----------------------------------------Method------------------------------------------#
	# On_Start_Clicked(): méthode (slot) appelée lors de la réception de l'événement "édition" de
	# l'éditeur de ligne "PortNumber"
	# ----------------------------------------------------------------------------------------#	        
    @pyqtSlot()
    def On_PortNumber_EditingFinished(self):
        regEx = QtCore.QRegExp("\\d*")
        arg1 = self.portNumber.text()
        if regEx.exactMatch(arg1) and int(arg1) <= 5050 and int(arg1) >= 5000:
            self.m_sPortNumber = arg1;
        else:
            self.portNumber.setText(self.m_sPortNumber);
            self.logger.warn(arg1 + ": Invalid Port Number Value, must be a number between 5000 and 5050")
        self.logger.debug("PortNumber has been changed")
            
    # ----------------------------------------Method------------------------------------------#
	# On_Start_Clicked(): méthode (slot) appelée lors de la réception de l'événement "édition" de
	# l'éditeur de ligne "Baudrate"
	# ----------------------------------------------------------------------------------------#        
    @pyqtSlot()
    def On_Baudrate_EditingFinished(self):
        regEx = QtCore.QRegExp("\\d*")
        arg1 = self.baudrate.text()
        if regEx.exactMatch(arg1) and int(arg1) > 0:
            self.m_sBaudrate = arg1;
        else:
            self.baudrate.setText(self.m_sBaudrate);
            self.logger.warn(arg1 + ": Invalid Baudrate Value, must be a positive number")
        self.logger.debug("Baudrate has been changed")
        
    # ----------------------------------------Method------------------------------------------#
	# InitializeGUI(): méthode appelée lors de l'initialisation de la classe.
	# Elle prend en paramètres "argumentsList", la liste des arguments du serveur
	# Elle permet d'initialiser l'interface graphique 
	# ----------------------------------------------------------------------------------------#
    def InitializeGUI(self, argumentsList):
                       
        self.m_sDefaultBaudrate = argumentsList[0]
        del argumentsList[0]
        self.m_sDefaultPortNumber = argumentsList[0]
        del argumentsList[0]
        self.IpServerAddress.setText(argumentsList[0])
        del argumentsList[0]
        self.m_sDefaultConnectorType = argumentsList[0]
        del argumentsList[0]
        self.m_sDefaultCsvFileName = argumentsList[0]
        del argumentsList[0]
        self.m_sDefaultSerialPortPath = argumentsList[0]
        del argumentsList[0]
        self.m_sDefaultRocketFileName = argumentsList[0]
        del argumentsList[0]
        self.m_sDefaultMapName = argumentsList[0]
        del argumentsList[0]       
        
        optionsValue = argumentsList[0]
        del argumentsList[0]
        
        if optionsValue & 1 != 0:
            self.m_sBaudrate = argumentsList[0]
            del argumentsList[0]
        else:
            self.m_sBaudrate = self.m_sDefaultBaudrate
        self.baudrate.setText(self.m_sBaudrate)
        
        if optionsValue & 2 != 0:
            self.m_sConnectorType = argumentsList[0]
            del argumentsList[0]
        else:
            self.m_sConnectorType = self.m_sDefaultConnectorType
        
        if optionsValue & 4 != 0:
            if self.m_sConnectorType == 'simulation':
                self.m_sCsvFileName = argumentsList[0]
                self.m_sSerialPortPath = self.m_sDefaultSerialPortPath
                del argumentsList[0]
            else:
                self.m_sSerialPortPath = argumentsList[0]
                self.m_sCsvFileName = self.m_sDefaultCsvFileName
                del argumentsList[0]
        else:
            self.m_sCsvFileName = self.m_sDefaultCsvFileName
            self.m_sSerialPortPath = self.m_sDefaultSerialPortPath
        self.csvFile.setCurrentText(self.m_sCsvFileName)
        self.serialPort.setCurrentText(self.m_sSerialPortPath)      
            
        if optionsValue & 8 != 0:
            self.m_sPortNumber = argumentsList[0]
            del argumentsList[0]            
        else:
            self.m_sPortNumber = self.m_sDefaultPortNumber
        self.portNumber.setText(self.m_sPortNumber) 
        
        if optionsValue & 16 != 0:
            self.m_sRocketFileName = argumentsList[0]
            del argumentsList[0]            
        else:
            self.m_sRocketFileName = self.m_sDefaultRocketFileName
        self.rocket.setCurrentText(self.m_sRocketFileName)
        
        if optionsValue & 32 != 0:
            self.m_sMapName = argumentsList[0]
            del argumentsList[0]            
        else:
            self.m_sMapName = self.m_sDefaultMapName
        self.map.setCurrentText(self.m_sMapName)
        
        self.SetCsvFileNameList()
        self.SetSerialPortPathList()
        self.SetRocketFileNameList()
        self.SetMapNameList()
        
        if self.m_sConnectorType == 'simulation':     
            self.simulation.setChecked(True)
            self.csvFile.setEnabled(True)
            self.serial.setChecked(False)
            self.serialPort.setEnabled(False)
            self.baudrate.setEnabled(False)
        else:
            self.serial.setChecked(True)
            self.simulation.setChecked(False)           
            self.serialPort.setEnabled(True)
            self.baudrate.setEnabled(True)
            self.csvFile.setEnabled(False)
        
        self.IpServerAddress.setAlignment(Qt.AlignCenter)
        self.IpServerAddress.setReadOnly(True)
        self.IpServerAddress.setStyleSheet("background-color: lightGray")
        
        self.Start.setStyleSheet("background-color: darkGreen")
        self.Set_default.setStyleSheet("background-color: lightGray")
        self.Quit.setStyleSheet("background-color: darkRed")
        
        self.DisplayLog_2.setReadOnly(True)
        self.DisplayLog_2.setStyleSheet("background-color: lightGray")
        self.DisplayLog_2.setAlignment(Qt.AlignCenter)
        self.DisplayLog_3.setReadOnly(True)
        self.DisplayLog_3.setStyleSheet("background-color: lightGray")
        self.DisplayLog_3.setAlignment(Qt.AlignCenter)
        self.DisplayLog_4.setReadOnly(True)
        self.DisplayLog_4.setStyleSheet("background-color: lightGray")
        self.DisplayLog_4.setAlignment(Qt.AlignCenter)
        self.DisplayLog_5.setReadOnly(True)        
        self.DisplayLog_5.setStyleSheet("background-color: lightGray")
        self.DisplayLog_5.setAlignment(Qt.AlignCenter)
        
    # ----------------------------------------Method------------------------------------------#
	# SetCsvFileNameList(): méthode appelée par la méthode InitializeGUI().
	# Elle permet d'initialiser la liste des nom des fichiers csv
	# ----------------------------------------------------------------------------------------#
    def SetCsvFileNameList(self):
        self.csvFile.clear()
        for file in os.listdir(self.csvPath):
            if file.endswith('.csv') and file != 'CANSid.csv':
                with open(os.path.join(self.csvPath, file), "r", encoding="ISO-8859-1") as csvFile:
                    readCSV = csv.reader(csvFile, delimiter=';')
                    row1 = next(readCSV)					
                    if readCSV and len(row1) >= 9 and "Temps (s)" in row1:				
                        self.csvFile.addItem(file)
        self.csvFile.setCurrentText(self.m_sCsvFileName)
        
    
    # ----------------------------------------Method------------------------------------------#
	# SetSerialPortPathList(): méthode appelée par la méthode InitializeGUI().
	# Elle permet d'initialiser la liste des ports série disponibles
	# ----------------------------------------------------------------------------------------# 
    def SetSerialPortPathList(self):
        self.serialPort.clear()
        self.serialPort.addItem("/dev/ttyUSB0")
        seriaPortPath = '/dev'
        regEx = QtCore.QRegExp("tty\\d*")        
        for file in os.listdir(seriaPortPath):
            filePath = seriaPortPath + '/' + file
            if file.startswith('tty') and not regEx.exactMatch(file)and filePath != "/dev/ttyUSB0"\
             and self.CheckIfSerialPortIsValid(filePath):
                self.serialPort.addItem(filePath)
        self.serialPort.setCurrentText(self.m_sSerialPortPath)
    
    # ----------------------------------------Method------------------------------------------#
	# SetRocketFileNameList(): méthode appelée par la méthode InitializeGUI().
	# Elle permet d'initialiser la liste des nom des fichiers xml
	# ----------------------------------------------------------------------------------------#
    def SetRocketFileNameList(self):
        self.rocket.clear()
        for file in os.listdir(self.rocketPath):
            if file.endswith('.xml'):
                self.rocket.addItem(file)
        self.rocket.setCurrentText(self.m_sRocketFileName)
    
    # ----------------------------------------Method------------------------------------------#
	# SetMapNameList(): méthode appelée par la méthode InitializeGUI().
	# Elle permet d'initialiser la liste des nom des cartes de géolocalisation
	# ----------------------------------------------------------------------------------------#
    def SetMapNameList(self):
        self.map.clear()
        for item in MapName:
            if item.name:
                self.map.addItem(item.name)
        self.map.setCurrentText(self.m_sMapName)
    
    # ----------------------------------------Method------------------------------------------#
	# UpdateParameters(): méthode appelée par la méthode On_Start_Clicked().
	# Elle permet de faire la mise à jour des paramètres du serveur
	# ----------------------------------------------------------------------------------------#
    def UpdateParameters(self):
        self.m_sCsvFileName = self.csvFile.currentText()
        self.m_sSerialPortPath = self.serialPort.currentText()
        self.m_sBaudrate = self.baudrate.text()
        self.m_sPortNumber = self.portNumber.text()
        self.m_sRocketFileName = self.rocket.currentText()
        self.m_sMapName = self.map.currentText()
    
          
    # ----------------------------------------Method------------------------------------------#
	# DisplayConnectedUsers(): méthode appelée par la méthode displayMessage() de la classe 
	# ConnectedUsersThread
	# Elle prend en paramètres "sMessage", une chaîne de caractères
	# Elle permet d'afficher le message (en paramèetre) dans l'éditeur de texte dédié à 
	# l'affichage des utilisateurs connectés
	# ----------------------------------------------------------------------------------------#	    
    def DisplayConnectedUsers(self, sMessage):
        self.ClearConnectedUsers()
        for user in sMessage.split('@'):
            if len(user.split(';')) >= 4:
                self.DisplayLog_2.append(user.split(';')[0])
                self.DisplayLog_3.append(user.split(';')[1])
                self.DisplayLog_4.append(user.split(';')[2])
                self.DisplayLog_5.append(user.split(';')[3])
            else:
                self.ClearConnectedUsers()
    # ----------------------------------------Method------------------------------------------#
    # DisplayConnectedUsers(): méthode appelée par la méthode DisplayConnectedUsers()
    # Elle permet d'effacer le contenu de l'éditeur de texte dédié à l'affichage des utilisateurs 
    # connectés
    # ----------------------------------------------------------------------------------------#	    
    def ClearConnectedUsers(self):
        self.DisplayLog_2.clear()
        self.DisplayLog_3.clear()
        self.DisplayLog_4.clear()
        self.DisplayLog_5.clear()
    
    # ----------------------------------------Method------------------------------------------#
    # CheckIfSerialPortIsValid(): méthode appelée par la méthode SetSerialPortPathList().
    # Elle prend en paramètres "serialPort", chemin vers le port série à utiliser
    # Elle de vérifier la validité du port série passé en paramètre et retourn vrai lorsque valide
    # ou faux sinon
    # ----------------------------------------------------------------------------------------#
    def CheckIfSerialPortIsValid(self, serialPort):
        ser = serial.Serial()
        ser.port = serialPort
        ser.baudrate = self.m_sDefaultBaudrate
        ser.bytesize = serial.EIGHTBITS #number of bits per bytes
        ser.parity = serial.PARITY_NONE #set parity check: no parity
        ser.stopbits = serial.STOPBITS_ONE #number of stop bits
        ser.timeout = None              #timeout block read
        try:
            ser.open()
            ser.close()
        except:
            return False		
        return True
    
    # ----------------------------------------Method------------------------------------------#
    # GetReader(): méthode appelée par la méthode SetSerialPortPathList().
    # Elle permet de retourner un le nom du fichier csv en mode simulation ou le lecteur série
    # en mode série
    # ----------------------------------------------------------------------------------------#
    def GetReader(self):
        if self.simulation.isChecked():
            return os.path.join(self.csvPath, self.csvFile.currentText())
        else:
            ser = serial.Serial()
            ser.port = self.serialPort.currentText()
            ser.baudrate = self.baudrate.text()
            ser.bytesize = serial.EIGHTBITS #number of bits per bytes
            ser.parity = serial.PARITY_NONE #set parity check: no parity
            ser.stopbits = serial.STOPBITS_ONE #number of stop bits
            ser.timeout = None              #timeout block read
            try:
                ser.open()
                ser.close()
            except serial.serialutil.SerialException:
                self.logger.warn(self.serialPort.currentText() + " : invalid serial port")
                sys.exit(1)		
            return ser

    # ----------------------------------------Method------------------------------------------#
    # GetLogger(): méthode appelée par la méthode __init__().
    # Elle prend en paramètres "logPath", chemin vers le dossier contenant les journaux du serveur
    # Elle permet de retourner un logger
    # ----------------------------------------------------------------------------------------#
    def GetLogger(self, logPath):
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
        self.DisplayLog.setFormatter(formatter)
        logFileName = str(datetime.datetime.now()) + '.log'
        if not os.path.exists(logPath):
            os.makedirs(logPath)	
        fileHdlr = logging.FileHandler(os.path.join(logPath, logFileName))
        fileHdlr.setFormatter(formatter)
        rootLogger = logging.getLogger()
        rootLogger.addHandler(self.DisplayLog)
        rootLogger.addHandler(fileHdlr)
        logger = logging.getLogger("myLogger")
        logger.setLevel(logging.DEBUG)
        return logger
        
    # ----------------------------------------Method------------------------------------------#
    # CreateXmlConfig(): méthode appelée par la méthode On_Start_Clicked().
    # Elle prend en paramètres "configPath", "configFile", "port", "rocketFile", "map"
    # Elle permet de créer le fichier xml de configuration de l'application Android
    # ----------------------------------------------------------------------------------------#    
    def CreateXmlConfig(self, configPath, configFile, port, rocketFile, map):
        if not os.path.exists(configPath):
            os.makedirs(configPath)
        config = ET.Element('config')
        ET.SubElement(config, "otherPort").text = str(port)
        tree = ET.ElementTree(config)
        ET.SubElement(config, "layout").text = rocketFile
        tree = ET.ElementTree(config)
        ET.SubElement(config, "map").text = map
        tree = ET.ElementTree(config)
        xmlFilePath = os.path.join(configPath, configFile)
        tree.write(xmlFilePath, pretty_print=True, xml_declaration=True, encoding="utf-8")
        
    # ----------------------------------------Method------------------------------------------#
    # DispayLogMessage(): méthode appelée par la méthode logger() des classes ReceiverThread, 
    # TransmitterThread, RestServer et SocketThread
    # Elle prend en paramètres "sMessage", une chaîne de caractères
    # Elle permet d'afficher le message (en paramèetre) dans l'éditeur de texte dédié à 
    # au journal des événements importants survenus au serveur
    # ----------------------------------------------------------------------------------------#	    
    def DispayLogMessage(self, logMessage):
        messageList = logMessage.split('@')
        if len(messageList) >= 2:
            if messageList[0] == 'error':
                self.logger.error(messageList[1])
            elif messageList[0] == 'warn':
                self.logger.warn(messageList[1])
            elif messageList[0] == 'debug':
                self.logger.debug(messageList[1])
            else:
                self.logger.info(messageList[1])
