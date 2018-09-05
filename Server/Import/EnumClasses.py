from enum import Enum

# ----------------------------------------CLASS----------------------------------------------#
# Classe ModuleType dérivée de la classe Enum
# Il s'agit de la classe permettant d'énumérer tous les types des modules
# -------------------------------------------------------------------------------------------#
class ModuleType(Enum):

	ADM = 0					# Avionics Deployment Module
	ADIRM = 3				# Air Data Intertial Reference Module
	ADLM = 4				# Avionics Data Logging Module
	APUM = 6				# Avionics Power Unit Module
	NUC = 7					# Ground station = serveur = pas un PCB
	GS = 7					# Ground station = serveur = pas un PCB
	MCD = 15				# Moduel for Control and Deployment
	AGRUM = 16				# Avionics GPS Radio Universal Module
	ADRMSAT = 17			# Avionics Deployment Radio Module SATellite
	ATM_MASTER = 18			# Avionics Thrust Module, master
	ATM_SLAVE = 19			# Avionics Thrust Module, slave
	UNKNOWN_MODULE = 0x1E
	ALL_MODULES = 0x1F		# Permet un broadcast CAN a tous les modules

# ----------------------------------------CLASS----------------------------------------------#
# Classe ModuleType dérivée de la classe Enum
# Il s'agit de la classe permettant d'énumérer tous les noms des cartes de géolocalisation
# -------------------------------------------------------------------------------------------#
class MapName(Enum):

	Spaceport_America = 0
	Motel_6 = 1
	Convention_Center = 2
	St_Pie_de_Guire = 3
