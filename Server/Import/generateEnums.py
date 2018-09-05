#!/usr/bin/python3
#
########################################################################################################################
#
#	Génère des enum C et Python avec les CANMsgID.
########################################################################################################################
#
#	Copyright 2015 Oronos Polytechnique. Tous droits réservés
#
########################################################################################################################

import os
import datetime as dt
from sys import stderr
from binascii import crc32


cSIDHFileHeader = """/*
 ******************************************************************************
 * CE FICHIER EST AUTOGÉNÉRÉ! NE PAS LE MODIFIER!
 * @file	CANSid.h
 * @author	Oronos Polytechnique
 * @version	V3.0.0
 * @brief	Définition des SIDs du CAN
 * @addtogroup CAN
 * @{
 ******************************************************************************
 *
 * Copyright 2014-"""+dt.datetime.now().strftime("%Y")+""". Oronos Polytechnique. All rights reserved.
 *
 ******************************************************************************
 */

#pragma once

/**
 ******************************************************************************
 * @enum CAN_MSGID
 *
 * Définition des identifiants de message sur le bus CAN.
 *
 ******************************************************************************
 */
typedef enum {
"""

cSIDHFileTrailer = """} CAN_MSGID;

/**
 ******************************************************************************
 * @}
 ******************************************************************************
 */
"""

cSIDCFileHeader = """/*
 ******************************************************************************
 * CE FICHIER EST AUTOGÉNÉRÉ! NE PAS LE MODIFIER!
 * @file	CANSid.c
 * @author	Frédéric Fortier
 * @version	V1.0.0
 * @brief	Types et magic bytes du CAN (qui correspondent au CRC32 du nom de l'enum)
 * @addtogroup CAN
 * @{
 ******************************************************************************
 *
 * Copyright """+dt.datetime.now().strftime("%Y")+""". Oronos Polytechnique. All rights reserved.
 *
 ******************************************************************************
 */

#include "CANSid.h"
#include "CANDefs.h"
#include <inttypes.h>

const uint8_t CANMsgDataTypes[2048] = {
"""

cSIDCFileMiddle =""" };

const unsigned magicBytes[2048] = {
"""

cSIDCFileTrailer = """};

/**
 ******************************************************************************
 * @}
 ******************************************************************************
 */
"""

pyHeader = """# CE FICHIER EST AUTO-GÉNÉRÉ! NE PAS LE MODIFIER!
# Copyright """ +dt.datetime.now().strftime("%Y")+""". Oronos Polytechnique. Tous droits réservés.

from enum import IntEnum, unique

@unique
class CANDataType(IntEnum):
	UNKNOWN = 0,
	INT = 1,
	FLOAT = 2,
	UNSIGNED = 3,
	TIMESTAMP = 10,
	MAGIC = 11,
	NONE = 15

@unique
class CANSid(IntEnum):"""

pyFileMiddle = """

CANMsgDataTypes = [(CANDataType.UNKNOWN, CANDataType.UNKNOWN) for i in range(2048)]
"""

cCommentChar = "// "				#On ne met pas de commentaire doxygen sur les commentaires qui font toute une ligne
pyCommentChar = "#"
tab = "	"

MSGID_LEN = 8
LLCList = [ 0 << MSGID_LEN, 1 << MSGID_LEN, 2 << MSGID_LEN, 3 << MSGID_LEN, 4 << MSGID_LEN, 5 << MSGID_LEN, 6 << MSGID_LEN, 7 << MSGID_LEN ]


def main():

	pyFile = open("Import/CANSid.py", "w", encoding="utf-8")
	#cSIDFile = open("CANSid.h", "w", encoding="utf-8")
	#cSIDCFile = open("CANSid.c", "w", encoding="utf-8")
	pyFile.write(pyHeader)
	#cSIDFile.write(cSIDHFileHeader)
	#cSIDCFile.write(cSIDCFileHeader)
	prevValue = int(0)
	channelIndex = 0
	cWriteString = ""		#Il va falloir enlever la dernière virgule de l'enum en C :(
	cTypeString = ""
	pyTypeString = ""
	magicWriteString = ""

	with open("./CSV/CANSid.csv", "r", encoding="utf-8") as f:
		#La première ligne ne contient que l'en-tête des colonnes pour être le fun dans excel
		f.readline()
		for line in f:

			# Ignore empty lines
			if line == "\n":
				continue
			try:
				(id, type1, type2, commentaire) = line.split(";")
			except ValueError as e:
				print("Bad line: " + line)
				raise e
			commentaire = commentaire[:-1]		#On enlève le saut de ligne de la fin de la ligne
			if id == "":
				prevValue = LLCList[channelIndex]
				channelIndex += 1
				cWriteString += ("\n" + tab + cCommentChar + commentaire + "\n")
				pyFile.write("\n" + tab + pyCommentChar + commentaire + "\n")
			else:
				valeur = prevValue + 1
				if commentaire == "":
					cComment = ""
					pyComment = ""
				else:
					cComment = tab + tab + cCommentChar + commentaire
					pyComment = tab + tab + pyCommentChar + commentaire
				cWriteString += (tab + id + " = " + str(valeur) + "," + cComment + "\n")
				pyFile.write(tab + id + " = " + str(valeur) + pyComment + "\n")

				cTypeString += (tab + "[" + id + "] = CAN_" + type1 + "_" + type2 + ",\n")

				pyTypeString += ("CANMsgDataTypes[CANSid." + id + "] = (CANDataType." + type1 + ", CANDataType." + type2 + ")\n")
				bytesID = bytes(id, "utf-8")
				crc = crc32(bytesID)

				magicWriteString += (tab + "[" + id + "] = " + hex(crc) + ",\n" )

				prevValue = valeur

	cWriteString = cWriteString[::-1].replace(";"[::-1], ""[::-1], 1)[::-1]		#On enlève le dernier , de l'enum
	cTypeString = cTypeString[::-1].replace(","[::-1], ""[::-1], 1)[::-1]
	magicWriteString = magicWriteString[::-1].replace(","[::-1], ""[::-1], 1)[::-1]
	#cSIDFile.write(cWriteString)
	#cSIDCFile.write(cTypeString)
	#cSIDCFile.write(cSIDCFileMiddle)
	#cSIDCFile.write(magicWriteString)
	#cSIDFile.write(cSIDHFileTrailer)
	#cSIDCFile.write(cSIDCFileTrailer)
	pyFile.write(pyFileMiddle)
	pyFile.write(pyTypeString)
	#cSIDFile.close()
	#cSIDCFile.close()
	pyFile.close()
	#print("Succès")


main()
