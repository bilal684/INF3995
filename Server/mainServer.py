#!/usr/bin/python3
import socket
import os
import platform
import sys, getopt
import serial
import netifaces
import signal
import queue
import time
import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from lxml import etree as ET
from Import.EnumClasses import MapName
from Import.serverGUI import ServerGUI


# ----------------------------------------CLASS----------------------------------------------#
# Programme principal main()
# Il permet de capturer les arguments entrés en ligne de commande et de les valider.
# Il permet aussi d'instancier un objet de la classe ServerGUI et d'afficher l'interface
# graphique.
# -------------------------------------------------------------------------------------------#	
def main(argv):
    DEFAULT_SERIAL_PORT = '/dev/ttyUSB0'
    DEFAULT_CSV_FILE = 'valkyrie_ii.csv'
    DEFAULT_CONNECTOR_TYPE = 'simulation'
    DEFAULT_ROCKET_FILE = '11_valkyrieM2.xml'
    DEFAULT_MAP_NAME = str(MapName(0).name) # default map name: Spaceport_America
    DEFAULT_CONFIG_FILE = 'config.xml'
    DEFAULT_PORT = 5050
    DEFAULT_BAUDRATE = 921600
    TIMEOUT = 5.0 # timeout for socket
    baudrateValue = DEFAULT_BAUDRATE
    connector_type = DEFAULT_CONNECTOR_TYPE
    connector_file = DEFAULT_CSV_FILE
    csvPath = './CSV' # folder path for csv files
    portNumber = DEFAULT_PORT
    mapName = DEFAULT_MAP_NAME
    rocketFile = DEFAULT_ROCKET_FILE
    rocketPath = './config/rockets' # folder path for xml rocket files
    configPath = './config' # folder path for xml config file
    configFile = DEFAULT_CONFIG_FILE
    logSuffix = '.log'
    logPath = './Log' # folder path for log files
    
    optionsValue = 0
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hb:c:f:s:r:m:",["help", "baudrate=", "connector_type=",\
        "connector_file=", "server=", "rocket=", "map="])
    except getopt.GetoptError:
        print('OptError: mainServer.py -h -b <baudrate> -c <connector_type> ' +\
                    '-f <connector_file> -s <port> -r <rocket> -m <map>')
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("Usage : mainServer.py [-h ] [-b BAUDRATE] [-c {serial, simulation}]\n" +\
                  "\t[-f CONNECTOR_FILE] [-s PORT] [-r ROCKET] [-m MAP]\n\n" +\
                  "Description :\n" +\
                  "\tProgramme serveur permettant d'avoir la communication avec\n" +\
                  "\tune fusee d'Oronos et des PC/tablettes client.\n\n" +\
                  "Arguments optionnels:\n" +\
                  "\t-h, --help\n" +\
                  "\t\tMessage d'aide et sortie immediate.\n" +\
                  "\t-b BAUDRATE, --baudrate BAUDRATE\n" +\
                  "\t\tBaudrate du port serie (connecteur serial seulement).\n" +\
                  "\t\t(Default : 921600)\n" +\
                  "\t-c {serial, simulation},--connector_type {serial, simulation}\n" +\
                  "\t\tSource des donnees a traiter. (Default : simulation)\n" +\
                  "\t-f CONNECTOR_FILE, --connector_file CONNECTOR_FILE\n" +\
                  "\t\tArgument pour le type de connecteur c'est-a-dire le\n" +\
                  "\t\tport serie COM si en mode serial (Default : /dev/ttyUSB0)\n" +\
                  "\t\tou le nom du fichier de donnees CSV pour le mode simulation\n" +\
                  "\t\t(Default : valkyrie_ii.csv)\n" +\
                  "\t-s [PORT], --server [PORT]\n" +\
                  "\t\tActive un server pour avoir plusieurs stations au sol.\n" +\
                  "\t\t(Default : 5050)\n" +\
                  "\t-r ROCKET, --rocket ROCKET\n" +\
                  "\t\tLe nom du fichier XML. Ex :\n" +\
                  "\t\t10_polaris.xml. (Default : 11_valkyrieM2 .xml)\n" +\
                  "\t-m MAP, --map MAP\n" +\
                  "\t\tLe nom de la carte faisant parti des noms de la classe\n" +\
                  "\t\tEnum MapName dans le fichier EnumClasses.py . Ex: Motel_6.\n" +\
                  "\t\t(Default : Spaceport_America)")
            sys.exit(0)
        elif opt in ("-b", "--baudrate"):
            if optionsValue & 1 != 0:
                print("Option -b (--baudrate) is entered more than once")
                sys.exit(1)
            try:
                baudrateValue = int(arg)				
                optionsValue |= 1
                if baudrateValue <= 0:
                    print("Invalid baud rate value: " + arg)
                    sys.exit(1)
            except ValueError:
                print("Invalid baud rate value: " + arg)
                sys.exit(1)
        elif opt in ("-c", "--connector_type"):			
            if optionsValue & 2 != 0:
                print("Option -c (--connector_type) is entered more than once")
                sys.exit(1)
            connector_type = arg
            optionsValue |= 2
        elif opt in ("-f", "--connector_file"):			
            if optionsValue & 4 != 0:
                print("Option -f (--connector_file) is entered more than once")
                sys.exit(1)
            connector_file = arg
            optionsValue |= 4
        elif opt in ("-s", "--server"):
            if optionsValue & 8 != 0:
                print("Option -s (--server) is entered more than once")
                sys.exit(1)
            try:
                portNumber = int(arg)
                optionsValue |= 8
                if portNumber < 5000 or portNumber > 5050:
                    print("Invalid server port value: " + arg + ". Server port must be 0-65535 and <> 80")
                    sys.exit(1)				
            except ValueError:
                print("Invalid server port value: " + arg)
                sys.exit(1)			
        elif opt in ("-r", "--rocket"):
            if optionsValue & 16 != 0:
                print("Option -r (--rocket) is entered more than once")
                sys.exit(1)
            rocketFile = arg
            optionsValue |= 16
            xmlFilePath = os.path.join(rocketPath, rocketFile)
            if not os.path.exists(xmlFilePath):
                print("File not found: " + xmlFilePath)
                sys.exit(2)
        elif opt in ("-m", "--map"):
            if optionsValue & 32 != 0:
                print("Option -m (--map) is entered more than once")
                sys.exit(1)
            mapName = arg
            optionsValue |= 32
            if not mapName in MapName.__members__:
                errorMessage = "Invalid map name: " + arg + '. Valid map name: '
                for item in MapName:
                    errorMessage += item.name + ' OR '
                print(errorMessage[:-4])
                sys.exit(1)
    
    xmlFilePath = os.path.join(rocketPath, rocketFile)
    if not os.path.exists(xmlFilePath):
        print("File not found: " + xmlFilePath)
        sys.exit(2)
	
    if platform.system().lower() == 'linux':
        try:
            ethernet = 'eth0'
            netifaces.ifaddresses(ethernet)			
        except:
                ethernet = 'wlo1'
                netifaces.ifaddresses(ethernet)
    elif platform.system().lower() == 'darwin':
        ethernet = 'en0'
        netifaces.ifaddresses(ethernet)		
    else:
        print('system platform: ' + platform.system() + ' does not support this program')
        sys.exit(1)	
	
    if connector_type.lower() == 'serial':
        if optionsValue & 4 == 0:
            connector_file = DEFAULT_SERIAL_PORT
        if not CheckIfSerialPortIsValid(connector_file, baudrateValue):
            print("Invalid serial port: " + connector_file)
            sys.exit(1)	
    elif connector_type.lower() == 'simulation':
            if optionsValue & 1 != 0: # baud rate received optional
                print('Baud rate value must be specified for serial mode only')
                sys.exit(1)
            elif ".csv" not in connector_file.lower(): # connector_file received optional
                print(connector_file + ' : Invalid CSV file name')
                sys.exit(1)
            else:
                csvFilePath = os.path.join(csvPath, connector_file)
            if not os.path.exists(csvFilePath):
                print("File not found: " + csvFilePath)
                sys.exit(2)
    else:
        print("Invalid connector type: " + connector_type + ". Must be \'serial\' or \'simulation\'")
        sys.exit(2)
    
    host = ''
    host = netifaces.ifaddresses(ethernet)[netifaces.AF_INET][0]['addr']
         
    argumentsList = []    
    argumentsList.append(str(DEFAULT_BAUDRATE))
    argumentsList.append(str(DEFAULT_PORT))
    argumentsList.append(host)
    argumentsList.append(DEFAULT_CONNECTOR_TYPE)    
    argumentsList.append(DEFAULT_CSV_FILE)
    argumentsList.append(DEFAULT_SERIAL_PORT)
    argumentsList.append(DEFAULT_ROCKET_FILE)
    argumentsList.append(DEFAULT_MAP_NAME)
    argumentsList.append(optionsValue)
    if optionsValue & 1 != 0:
        argumentsList.append(str(baudrateValue))
    if optionsValue & 2 != 0:
        argumentsList.append(connector_type)
    if optionsValue & 4 != 0:
        argumentsList.append(connector_file)
    if optionsValue & 8 != 0:
        argumentsList.append(str(portNumber))
    if optionsValue & 16 != 0:
        argumentsList.append(rocketFile)
    if optionsValue & 32 != 0:
        argumentsList.append(mapName)
        
    
    myApp = QApplication(sys.argv)    
    myWidget = ServerGUI(argumentsList, csvPath, rocketPath, logPath, configPath, configFile)
    pal = myWidget.palette();
    pal.setColor(myWidget.backgroundRole(), Qt.darkGray)
    myWidget.setAutoFillBackground(True)
    myWidget.setPalette(pal)
    myWidget.show()
    os.system('clear')
    sys.exit(myApp.exec_())

	

# ----------------------------------------Method------------------------------------------#
# CheckIfSerialPortIsValid(): méthode appelée par la méthode main().
# Elle prend en paramètres "serialPort", chemin vers le port série à utiliser
# et "baudrate", la valeur de la vitesse de transmission de bits utilisée par le port série
# Elle de vérifier la validité du port série passé en paramètre et retourn vrai lorsque valide
# ou faux sinon
# ----------------------------------------------------------------------------------------#
def CheckIfSerialPortIsValid(serialPort, baudrate):
		ser = serial.Serial()
		ser.port = serialPort
		ser.baudrate = baudrate
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


	
     
if __name__ == "__main__":
   main(sys.argv[1:])
