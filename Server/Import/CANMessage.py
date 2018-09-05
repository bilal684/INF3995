from Import.EnumClasses import ModuleType
from Import.CANSid import CANSid
from Import.CANSid import CANDataType
from Import.CANSid import CANMsgDataTypes
import logging

class CANMessage:

	def __init__(self, msgID , destID, destSerial, srcID, srcSerial , data1, data2):
		
		try:
			if type(msgID) is not CANSid:		
				if type(msgID) is str:			#On reçoit une string, on le fait correspondre à l'enum
					msgID = CANSid[msgID]
				else:							#On reçoit un numéro, on le fait correspondre à l'enum
					msgID = CANSid(msgID)
		except:
			if type(msgID) is not str:
					msgID = str(msgID)
		
		try:	
			if type(destID) is not ModuleType:
				if type(destID) is str:
					try:
						destID = ModuleType[destID]
					except:
						destID = ModuleType.UNKNOWN_MODULE
				else:
					destID = ModuleType(destID)	
		except:
			destID = ModuleType.UNKNOWN_MODULE		
			
		try:	
			if type(srcID) is not ModuleType:
				if type(srcID) is str:
					try:
						srcID = ModuleType[srcID]
					except:
						srcID = ModuleType.UNKNOWN_MODULE
				else:
					srcID = ModuleType(srcID)	
		except:
			srcID = ModuleType.UNKNOWN_MODULE					

		self.msgID = msgID
		self.destID = destID
		self.destSerial = destSerial
		self.srcID = srcID
		self.srcSerial = srcSerial		
		self.data1 = data1
		self.data2 = data2
		self.dataType1 = CANMsgDataTypes[self.msgID][0]
		self.dataType2 = CANMsgDataTypes[self.msgID][1]
