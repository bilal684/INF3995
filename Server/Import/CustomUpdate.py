"""
	File: CustomUpdate.py
	Desc: Contains all the functions that are called in the XMLs.
"""

from time import time
from typing import Optional
from Import.CANSid import CANSid
from Import.EnumClasses import ModuleType
from Import.CANMessage import CANMessage
#from DataInterpretation.Moteur.MotorStatusStruct import MotorSlaveStatusStruct
#from DataInterpretation.Moteur.Actuateur.Actuateur import State as ActuatorState
from Import.Units import Units

class CustomUpdate:
	altMax = {}
	lastRampAlt = {}

	"""
		Custom Update Functions
	"""

	@staticmethod
	def armingStatusUpdate(CANMsg, unused):
		armingStatus = int(CANMsg.data1)
		if armingStatus == 0:
			return "DISARMED"
		elif armingStatus == 1:
			return "ARMED"
		else:
			return "UNKNOWN"

	@staticmethod
	def admStateUpdate(CANMsg, unused):
		admState = int(CANMsg.data1)
		if admState == 0:
			return "INIT"
		elif admState == 1:
			return "ARMING"
		elif admState == 2:
			return "LAUNCH_DETECT"
		elif admState == 3:
			return "MACH_DELAY"
		elif admState == 4:
			return "APOGEE"
		elif admState == 5:
			return "MAIN_CHUTE_ALTITUDE"
		elif admState == 6:
			return "SAFE_MODE"
		else:
			return "UNKNOWN"

	@staticmethod
	def pressToAlt(CANMsg: CANMessage, unused):
		alt_f = Units.pascalToFeet(float(CANMsg.data1)) - ( CustomUpdate.lastRampAlt[(CANMsg.srcID, CANMsg.srcSerial)]
									if (CANMsg.srcID, CANMsg.srcSerial) in CustomUpdate.lastRampAlt else  0)
		return ("{:." + str(0) + "f}").format(alt_f) + " '"

	@staticmethod
	def rampAlt(CANMsg: CANMessage, unused):
		ramp_alt_f = float(CANMsg.data1) * Units.M_TO_FT
		CustomUpdate.lastRampAlt[(CANMsg.srcID, CANMsg.srcSerial)] = ramp_alt_f
		# HACK HACK HACK
		if CANMsg.srcID == ModuleType.ADM and CANMsg.srcSerial == 1:
			CustomUpdate.lastRampAlt[(ModuleType.ADIRM, 0)] = ramp_alt_f
		return ("{:." + str(0) + "f}").format(ramp_alt_f) + " '"

	@staticmethod
	def apogeeDetect(CANMsg: CANMessage, unused):
		if (CANMsg.srcID, CANMsg.srcSerial) not in CustomUpdate.altMax:
			CustomUpdate.altMax[(CANMsg.srcID, CANMsg.srcSerial)] = -float('inf')

		alt_f = -float('inf')
		if (CANMsg.srcID, CANMsg.srcSerial) in CustomUpdate.lastRampAlt:
			alt_f = Units.pascalToFeet(float(CANMsg.data1)) - CustomUpdate.lastRampAlt[(CANMsg.srcID, CANMsg.srcSerial)]
			
		if alt_f > CustomUpdate.altMax[(CANMsg.srcID, CANMsg.srcSerial)]:
			CustomUpdate.altMax[(CANMsg.srcID, CANMsg.srcSerial)] = alt_f
		return ("{:." + str(0) + "f}").format(CustomUpdate.altMax[(CANMsg.srcID, CANMsg.srcSerial)]) + " '"

	@staticmethod
	def oneWire(CANMsg: CANMessage, addr : str):
		""" Update the oneWire data if the CAN corresponds to the selected address. """
		return ("{:." + str(2) + "f}").format(CANMsg.data2) + " C" if CANMsg.data1 == int(addr, 16) else None

	@staticmethod
	def admBWVoltsToOhms(volts: float) -> float:
		conv = 3.5 * volts / 1000
		return conv if conv < 11 else float('inf')

	@staticmethod
	def admBWVoltsToOhmsString(CANMsg: CANMessage, unused) -> str:
		return ("{:." + str(1) + "f}").format(CustomUpdate.admBWVoltsToOhms(CANMsg.data1)) + " Ω"

	@staticmethod
	def meterToFoot(CANMsg: CANMessage, unused):
		return ("{:." + str(0) + "f}").format(float(CANMsg.data1) * 3.28084) + " '"

	@staticmethod
	def footToMeter(CANMsg: CANMessage, unused):
		return ("{:." + str(0) + "f}").format(float(CANMsg.data1) * 0.3048) + " m"

	@staticmethod
	def SDSpaceLeft(CANMsg: CANMessage, unused):
		#L'espace restant sur la carte SD est envoyé en ko
		if CANMsg.data1 < 0:		#Une erreur
			return "ERREUR"
		elif CANMsg.data1 < 10*1024:		#On envoie en ko
			return "{:.0f}".format(CANMsg.data1) + " ko"
		elif CANMsg.data1 < 1024*1024:
			return "{:.2f}".format(CANMsg.data1 / 1024) + " Mo"
		else:
			return "{:.2f}".format(CANMsg.data1 / (1024 * 1024)) + " Go"

	@staticmethod
	def SDBytesWritten(CANMsg: CANMessage, unused):
		#L'espace écrit est envoyé en octets
		if CANMsg.data1 < 1024 * 1024:
			return "{:.0f}".format(CANMsg.data1 /1024) + " ko"
		elif CANMsg.data1 < 1024 * 1024 * 1024:
			return "{:.2f}".format(CANMsg.data1 / (1024*1024)) + " Mo"
		else:
			return "{:.2f}".format(CANMsg.data1 / (1024*1024*1024)) + " Go"


	""" ---------- Motor ---------- """

	@staticmethod
	def armingStatusUpdate(CANMsg : CANMessage, unused : None) -> str:
		armingStatus = int(CANMsg.data1)
		if armingStatus == 0:
			return "DISARMED"
		elif armingStatus == 1:
			return "ARMED"
		else:
			return "UNKNOWN"

	@staticmethod
	def getFuelingValveText(CANMsg : CANMessage, unused) -> str:
		#enumVal = MotorSlaveStatusStruct(CANMsg.data1).fuelingValveStatus
		#state = ActuatorState(enumVal)
		return ''#state.name

	@staticmethod
	def getFuelingConnexionText(CANMsg : CANMessage, unused) -> str:
		#enumVal = MotorSlaveStatusStruct(CANMsg.data1).connectionStatus
		#state = ActuatorState(enumVal)
		return ''#state.name

	@staticmethod
	def getWatchdogTimePrettyString(CANMsg: CANMessage, unused) -> str:
		totalTime_ms = CANMsg.data1
		milliseconds = totalTime_ms % 1000
		seconds = int(totalTime_ms / 1000) % 60
		minutes = int(totalTime_ms / 60000)
		return str(minutes) + ":" +  (str(seconds) if seconds > 9 else "0" + str(seconds)) #+ "." + str(milliseconds)

	@staticmethod
	def getFuelingValveLockText(CANMsg: CANMessage, unused) -> str:
		return "LOCKED" if CustomUpdate.isFuelingValveLocked(CANMsg) else "UNLOCKED"

	@staticmethod
	def getFuelingConnexionLockText(CANMsg: CANMessage, unused) -> str:
		return "LOCKED" if CustomUpdate.isFuelingConnexionLocked(CANMsg) else "UNLOCKED"

	""" ---------- End Motor ---------- """

	"""
		Custom Acceptable Functions
	"""

	@staticmethod
	def isBWOhmAcceptable(CANMsg: CANMessage) -> bool:
		return 4.0 < CustomUpdate.admBWVoltsToOhms(CANMsg.data1) < 6.5

	@staticmethod
	def oneWireAcceptable(CANMsg: CANMessage) -> bool:
		return 15.0 < (CANMsg.data2) < 65.0


	""" ---------- Motor ---------- """

	@staticmethod
	def isFuelingValveNominal(CANMsg : CANMessage) -> bool:
		#enumVal = MotorSlaveStatusStruct(CANMsg.data1).fuelingValveStatus
		#state = ActuatorState(enumVal)
		return False #if state == ActuatorState.STUCK else True

	@staticmethod
	def isFuelingConnexionNominal(CANMsg : CANMessage) -> bool:
		#enumVal = MotorSlaveStatusStruct(CANMsg.data1).connectionStatus
		#state = ActuatorState(enumVal)
		return False #if state == ActuatorState.STUCK or state == ActuatorState.OPEN else True

	@staticmethod
	def isFuelingValveLocked(CANMsg: CANMessage) -> bool:
		return False #MotorSlaveStatusStruct(CANMsg.data1).fuelLineLocked

	@staticmethod
	def isNominal(CANMsg: CANMessage) -> bool:
		return False #MotorSlaveStatusStruct(CANMsg.data1).nominal

	@staticmethod
	def isNominal_typechecked(CANMsg: CANMessage) -> Optional[bool]:
		if CANMsg.msgID == CANSid.MOTOR_SLAVE_STATUS:
			return CustomUpdate.isNominal(CANMsg)
		else:
			return None

	@staticmethod
	def isFuelingConnexionLocked(CANMsg: CANMessage) -> bool:
		return False #MotorSlaveStatusStruct(CANMsg.data1).disconnectLocked

	@staticmethod
	def isBWOhmAcceptableForMotor(CANMsg : CANMessage) -> bool:
		return 1.5 < CustomUpdate.admBWVoltsToOhms(CANMsg.data1) < 2.5

	""" ---------- End Motor ---------- """

	def __init__(self):
		# Nothing to see here
		pass
