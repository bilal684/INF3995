# CE FICHIER EST AUTO-GÉNÉRÉ! NE PAS LE MODIFIER!
# Copyright 2018. Oronos Polytechnique. Tous droits réservés.

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
class CANSid(IntEnum):
	#Emergency Event data
	CANSID_RESERVED_1 = 1		#Don't use 0x1 for any command
	COMMAND_EMERGENCY_DEPLOY_DROGUE = 2		#(To the rocket) Emergency deploy drogue parachute
	COMMAND_EMERGENCY_DEPLOY_MAIN = 3		#(To the rocket) Emergency deploy main parachute
	MOTOR_EMERGENCY_VENT = 4		#(To the rocket) Vent motor ASAP, Data1 = 0 -> close vent
	MOTOR_FUELING_STANDBY = 5		#(To the rocket) Stop fueling and everything else, standby until further instructions
	MOTOR_MANUAL_START = 6		#(To the rocket) Start the motor manually. Note that the motor needs to be in ignition detection mode, and the option must be allowed. Data1 = 0 -> close motor valve
	MOTOR_ALLOW_MANUAL_START = 7		#(To the rocket) Data1 = 0 -> disallow manual start (default), Data2 = 0xDEADBEEF -> allow manual start.
	MOTOR_OVERRIDE_LAUNCH_READINESS = 8		#(To the rocket) Sets the imminent launch status. Data1 = 0xDEADBEEF -> override, Data2 = 0 -> non-override 

	#Safety/critical data
	COMMAND_DISARM = 257		#(To the rocket) Software disarm the recovery system
	COMMAND_ARM = 258		#(To the rocket) Software arm the recovery system
	COMMAND_UNLOCK = 259		#(To the rocket) Unlock le recovery system, allowing it to be disarmed
	COMMAND_LOCK = 260		#(To the rocket) Lock le recovery system, preventing it from being armed
	LVDM_CANNOT_TRIGGER_NOT_ARMED = 261		#Recovery system cannot and will not try to trigger because it is not armed
	LVDM_LOCKED_CANNOT_DISARM = 262		#Recovery system cannot be disarmed because it is in the locked state
	LVDM_ARMING_STATUS = 263		#Arming state according to the ARMING_STATE enum
	LVDM_EMERGENCY_KABOOM_CALLED = 264		#The LVDMTrigger function was called
	LVDM_TRIGGERED = 265		#The LVDMTrigger function returned EXIT_SUCCESS
	LVDM_CHARGES_BURNT = 266		#The recovery system detected a successful trigger
	LVDM_STATE = 267		#Recovery state according to the RECOVERY STATE enum
	LVDM_DIAGNOSTIC_FAILURE = 268		#A recovery init diagnostic failed. Error code comes from the RECOVERY_DIAGNOSTIC_FAILURE enum
	LVDM_RAMP_ALT = 269		#Launch ramp altitude in meters
	LVDM_ACKNOWLEDGE = 270		#Recovery system acknowledged a command. Data1 = CANSID of acknowledged command
	LVDM_LOCKED = 271		#Number of milliseconds until the recovery system will be unlocked, or 0 if unlocked
	VOTING_VSTRUCT_OVERFLOW = 272		#Error message. Voting struct overflow for altitude calculation
	VOTING_VSTRUCT_UPDATE_FAILURE = 273		#Error message. Voting struct update failure
	MOTOR_OPTION_IS_LOCKED = 274		#The option is locked: the override must be activated first. Data1 = option in question
	MOTOR_STATUS = 275		#Motor status (first param is of type MotorStatusStruct)
	MOTOR_SLAVE_STATUS = 276		#Motor slave (ie. on the ground) status (first param is of type MotorSlaveStatusStruct)
	MOTOR_RESERVED1 = 277
	MOTOR_FUELING_CONTROL = 278		# 0xDEADBEEF : Open fueling control, 0: close fueling control
	MOTOR_LAUNCH_IMMINENT = 279		# Launch imminent: injection mode is now automatic
	MOTOR_SET_STATE = 280		# Sets the state of the motor to Data1 if authorized
	MOTOR_SET_STATE_OVERRIDE = 281		# Sets the state of the motor to Data1
	MODULE_CRITICAL_FAILURE = 282		#MCU encountered unrecoverable error and will reboot in 1 second.
	CUBESAT_CANNON = 283		#Unused

	#Time-sensitive data
	COMMAND_RESET_MCU = 513		#(To the rocket) Reset the MCU
	LVDM_HALL_ACKNOWLEDGE = 514		#Input switch activated on the recovery system. Data1 = switch number. There are 4 switches
	TIMER_SET = 515		#All MCUs should set their millisecond timer to the value of Data1
	CURRENT_FATTIME = 516		#(To the rocket) Unix timestamp
	LVDM_BRIDGEWIRE_RES_DROGUE = 517		#Charges connection status (Bridgewire resistors) (ohm) for drogue parachute
	LVDM_BRIDGEWIRE_RES_MAIN = 518		#Charges connection status (Bridgewire resistors) (ohm) for main parachute
	MOTOR_TANK_TEMP = 519		#Rocket tank temperature in Celsius
	MOTOR_TANK_PRESS = 520		#Rocket tank pressure in PSI
	MOTOR_COMBUSTION_CHAMBER_TEMP = 521		#Combustion chamber (ie. in the grain) temperature in Celsius. Might be imprecise once the motor is started.
	MOTOR_VENT_TEMP = 522		#Vent pipe temperature in C
	MOTOR_ACTUATOR_VOLTS = 523		#Actuator input voltage
	BAR_PRESS1 = 524		#Barometric Pressure (Pascal)
	BAR_PRESS2 = 525		#Barometric Pressure (Pascal)
	RADIO_CONTROL = 526		#(To the rocket) To control the radio driver
	RADIO_ACKNOWLEDGE = 527		#Acknowledge of a RADIO_CONTROL message
	SD_ENABLE_LOGGING = 528		#Data1 = (bool)enable
	LOGGING_ACKNOWLEDGE = 529		#Acknowledge of a SD_ENABLE_LOGGING message

	#Normal Operation Data
	LSM_ACC_X = 769		#LSM303D accel on X axis in Gs
	LSM_ACC_Y = 770		#LSM303D accel on Y axis in Gs
	LSM_ACC_Z = 771		#LSM303D accel on Z axis in Gs
	ADXL_ACC_X = 772		#ADXL375 accel on X axis in Gs
	ADXL_ACC_Y = 773		#ADXL375 accel on Y axis in Gs
	ADXL_ACC_Z = 774		#ADXL375 accel on Z axis in Gs
	ICM_ACC_X = 775		#ICM20608 accel on X axis in Gs
	ICM_ACC_Y = 776		#ICM20608 accel on Y axis in Gs
	ICM_ACC_Z = 777		#ICM20608 accel on Z axis in Gs
	LSM_MAGN_FIELD_X = 778		#LSM303D magnetic field on X axis in Gauss
	LSM_MAGN_FIELD_Y = 779		#LSM303D magnetic field on Y axis in Gauss
	LSM_MAGN_FIELD_Z = 780		#LSM303D magnetic field on Z axis in Gauss
	L3G_RATE_X = 781		#L3GD20 angular rate on X axis in deg/s
	L3G_RATE_Y = 782		#L3GD20 angular rate on Y axis in deg/s
	L3G_RATE_Z = 783		#L3GD20 angular rate on Z axis in deg/s
	FANCY_RATE_X = 784		#ADXRS453 angular rate on X axis in deg/s
	FANCY_RATE_Y = 785		#ADXRS453 angular rate on Y axis in deg/s
	FANCY_RATE_Z = 786		#ADXRS453 angular rate on Z axis in deg/s
	ICM_RATE_X = 787		#ICM20608 angular rate on X axis in deg/s
	ICM_RATE_Y = 788		#ICM20608 angular rate on Y axis in deg/s
	ICM_RATE_Z = 789		#ICM20608 angular rate on Z axis in deg/s
	FILTERED_RATE_X = 790		#Unused
	FILTERED_RATE_Y = 791		#Unused
	FILTERED_RATE_Z = 792		#Unused
	TEMPERATURE = 793		#Temperature in C
	BAR_TEMPERATURE1 = 794		#MS5607-1 temperature in C
	BAR_TEMPERATURE2 = 795		#MS5607-2 temperature in C
	ONE_WIRE_TEMPERATURE = 796		#Data1 = thermometer ID, Data2 = temp in C
	GPS1_LATITUDE = 797		#(deg)
	GPS2_LATITUDE = 798		#(deg)
	GPS1_LONGITUDE = 799		#(deg)
	GPS2_LONGITUDE = 800		#(deg)
	GPS1_ALT_MSL = 801		#gps altitude msl (m)
	GPS2_ALT_MSL = 802		#gps altitude msl (m)
	GPS1_GND_SPEED = 803		#GPS ground speed (m/s)
	GPS2_GND_SPEED = 804		#GPS ground speed (m/s)
	GPS1_FIX_QUAL = 805		#gps fix quality
	GPS2_FIX_QUAL = 806		#gps fix quality
	GPS1_DATE_TIME = 807		#gps time since UTC beginning of day (s)
	GPS2_DATE_TIME = 808		#gps time since UTC beginning of day (s)
	GPS1_NB_SAT = 809		#number of satellites used
	GPS2_NB_SAT = 810		#number of satellites used
	GPS1_TRACK_ANG = 811		#GPS track angle (geographic) (deg)
	GPS2_TRACK_ANG = 812		#GPS track angle (geographic) (deg)
	GPS1_MAGN_VAR_TRACK = 813		#GPS magnetic variation and tracking (deg)
	GPS2_MAGN_VAR = 814		#GPS magnetic variation and tracking (deg)
	MOTOR_WATCHDOG_TIME_LEFT = 815		#Time left to the auto-vent watchdog timer (in case of comms failure) of the motor.
	MOTOR_DISCONNECT_FUELING = 816		#(To the rocket) Disconnects the fueling line if allowed
	MOTOR_OVERRIDE_DISCONNECTION_PROTECTION = 817		#(To the rocket) Data1 = (bool)protection_active
	MOTOR_SET_FUELING_LOCK = 818		#(To the rocket) Data1 = (bool)fueling_locked
	STATUS_LATCH_RESET = 819		#(To the rocket) Reset status LEDs
	PUM_3V3_CURRENT = 820
	PUM_5V_CURRENT = 821
	PUM_BAT1_CURRENT = 822
	PUM_BAT2_CURRENT = 823
	PUM_BAT3_CURRENT = 824
	PUM_VBAT1 = 825
	PUM_VBAT2 = 826
	PUM_VBAT3 = 827
	PUM_45V_CHARGED = 828
	RPM_VOLTAGE = 829
	RPM_CURRENT = 830
	RPM_45V = 831
	RADIO_STATS = 832
	ERR_CAN_GOT_BAD_MAGIC_BYTES = 833		#(premier paramètre = SID du message)
	ERR_CAN_SWITCHING_BUS = 834		# (premier paramètre = faulty bus (enum CAN_MODULE_ID casté))
	CALIB_SENSOR = 835		#Le premier paramètre est le SensorID du capteur
	LVDM_CHARGED = 836
	MPU_ACC_X = 837
	MPU_ACC_Y = 838
	MPU_ACC_Z = 839
	MPU_RATE_X = 840
	MPU_RATE_Y = 841
	MPU_RATE_Z = 842
	MPU_MAGN_FIELD_X = 843
	MPU_MAGN_FIELD_Y = 844
	MPU_MAGN_FIELD_Z = 845
	SL_ALTITUDE = 846

	#Node-service channel
	MODULE_BASE_INIT_SUCCESS = 1025		#Ne devrait contenir qu'un paramètre, le temps que l'initalisation a pris. Envoyé à la fin de oronosBaseInit()
	MODULE_SPECIFIC_INIT_SUCCESS = 1026		#Ne devrait contenir qu'un paramètre, le temps que l'initalisation a pris. Envoyé lorsque le module a terminé le setup de ses capteurs, etc.
	MODULE_SPECIFIC_INIT_RECOVERABLE_ERROR = 1027		# Principalement pour l'ADIRM. Indique une erreur, mais dont on peut récupérer. Data1 dépend du module.
	MODULE_SPECIFIC_INIT_FAILURE = 1028		# Lorsqu'un module n'a pas réussi son initialisation et ne peut pas fonctionner correctement
	MODULE_HEARTBEAT = 1029		#Heartbeat module, envoyé régulièrement.
	MODULE_GET_STATUS = 1030		#Requête de se faire envoyer le statut du module
	SD_CARD_WRITE_ERROR = 1031		#Une erreur d'écriture de la SD c'est produite. Des données ont été perdues.
	GS_UART_WRITE_ERROR = 1032		#Une erreur d'écriture par UART vers le GS c'est produite. Des données ont été perdues.
	GS_UART_READ_ERROR = 1033		#Une erreur de lecture par UART vers le GS c'est produite. Des données ont été perdues.
	ADIRM_DATA_QUEUE_FULL = 1034		# La queue d'envoi vers SD de l'ADIRM est full. Des données ont été perdues.
	SD_CARD_SPACE_LEFT = 1035		#Retourne l'espace restant (en *ko*) sur la carte SD, ou -1 s'il y a une erreur.
	SD_TOTAL_BYTES_WRITTEN = 1036		#Retourne le nombre de bytes écrits par le module depuis le dernier reset.
	SENSOR_CALIB_X = 1037		#Sensor auto-calibrated at this value (raw sensor unit). Second param is SensorID (defined in Sensor.h)
	SENSOR_CALIB_Y = 1038		#Sensor auto-calibrated at this value (raw sensor unit). Second param is SensorID (defined in Sensor.h)
	SENSOR_CALIB_Z = 1039		#Sensor auto-calibrated at this value (raw sensor unit). Second param is SensorID (defined in Sensor.h)
	MODULE_POS = 1040
	MODULE_NB = 1041
	COMMAND_REQ_MOD_POS_NB = 1042

	#User-defined Channel

	#Test and maintenance Channel
	CAN_TEST_INT_MAGIC = 1537
	CAN_TEST_INT_TIMESTAMP = 1538
	CAN_TEST_INT_INT = 1539
	CAN_TEST_INT_FLOAT = 1540
	CAN_TEST_INT_UNSIGNED = 1541
	CAN_TEST_FLOAT_MAGIC = 1542
	CAN_TEST_FLOAT_TIMESTAMP = 1543
	CAN_TEST_FLOAT_INT = 1544
	CAN_TEST_FLOAT_FLOAT = 1545
	CAN_TEST_FLOAT_UNSIGNED = 1546
	CAN_TEST_UNSIGNED_MAGIC = 1547
	CAN_TEST_UNSIGNED_TIMESTAMP = 1548
	CAN_TEST_UNSIGNED_INT = 1549
	CAN_TEST_UNSIGNED_FLOAT = 1550
	CAN_TEST_UNSIGNED_UNSIGNED = 1551
	CAN_TEST_MAGIC_NONE = 1552
	CAN_TEST_TIMESTAMP_MAGIC = 1553


CANMsgDataTypes = [(CANDataType.UNKNOWN, CANDataType.UNKNOWN) for i in range(2048)]
CANMsgDataTypes[CANSid.CANSID_RESERVED_1] = (CANDataType.MAGIC, CANDataType.NONE)
CANMsgDataTypes[CANSid.COMMAND_EMERGENCY_DEPLOY_DROGUE] = (CANDataType.MAGIC, CANDataType.NONE)
CANMsgDataTypes[CANSid.COMMAND_EMERGENCY_DEPLOY_MAIN] = (CANDataType.MAGIC, CANDataType.NONE)
CANMsgDataTypes[CANSid.MOTOR_EMERGENCY_VENT] = (CANDataType.UNSIGNED, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.MOTOR_FUELING_STANDBY] = (CANDataType.MAGIC, CANDataType.NONE)
CANMsgDataTypes[CANSid.MOTOR_MANUAL_START] = (CANDataType.UNSIGNED, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.MOTOR_ALLOW_MANUAL_START] = (CANDataType.UNSIGNED, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.MOTOR_OVERRIDE_LAUNCH_READINESS] = (CANDataType.UNSIGNED, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.COMMAND_DISARM] = (CANDataType.MAGIC, CANDataType.NONE)
CANMsgDataTypes[CANSid.COMMAND_ARM] = (CANDataType.MAGIC, CANDataType.NONE)
CANMsgDataTypes[CANSid.COMMAND_UNLOCK] = (CANDataType.MAGIC, CANDataType.NONE)
CANMsgDataTypes[CANSid.COMMAND_LOCK] = (CANDataType.MAGIC, CANDataType.NONE)
CANMsgDataTypes[CANSid.LVDM_CANNOT_TRIGGER_NOT_ARMED] = (CANDataType.TIMESTAMP, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.LVDM_LOCKED_CANNOT_DISARM] = (CANDataType.TIMESTAMP, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.LVDM_ARMING_STATUS] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.LVDM_EMERGENCY_KABOOM_CALLED] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.LVDM_TRIGGERED] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.LVDM_CHARGES_BURNT] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.LVDM_STATE] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.LVDM_DIAGNOSTIC_FAILURE] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.LVDM_RAMP_ALT] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.LVDM_ACKNOWLEDGE] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.LVDM_LOCKED] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.VOTING_VSTRUCT_OVERFLOW] = (CANDataType.TIMESTAMP, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.VOTING_VSTRUCT_UPDATE_FAILURE] = (CANDataType.TIMESTAMP, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.MOTOR_OPTION_IS_LOCKED] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MOTOR_STATUS] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MOTOR_SLAVE_STATUS] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MOTOR_RESERVED1] = (CANDataType.MAGIC, CANDataType.NONE)
CANMsgDataTypes[CANSid.MOTOR_FUELING_CONTROL] = (CANDataType.UNSIGNED, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.MOTOR_LAUNCH_IMMINENT] = (CANDataType.MAGIC, CANDataType.NONE)
CANMsgDataTypes[CANSid.MOTOR_SET_STATE] = (CANDataType.UNSIGNED, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.MOTOR_SET_STATE_OVERRIDE] = (CANDataType.UNSIGNED, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.MODULE_CRITICAL_FAILURE] = (CANDataType.UNSIGNED, CANDataType.UNSIGNED)
CANMsgDataTypes[CANSid.CUBESAT_CANNON] = (CANDataType.MAGIC, CANDataType.NONE)
CANMsgDataTypes[CANSid.COMMAND_RESET_MCU] = (CANDataType.MAGIC, CANDataType.NONE)
CANMsgDataTypes[CANSid.LVDM_HALL_ACKNOWLEDGE] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.TIMER_SET] = (CANDataType.UNSIGNED, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.CURRENT_FATTIME] = (CANDataType.UNSIGNED, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.LVDM_BRIDGEWIRE_RES_DROGUE] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.LVDM_BRIDGEWIRE_RES_MAIN] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MOTOR_TANK_TEMP] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MOTOR_TANK_PRESS] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MOTOR_COMBUSTION_CHAMBER_TEMP] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MOTOR_VENT_TEMP] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MOTOR_ACTUATOR_VOLTS] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.BAR_PRESS1] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.BAR_PRESS2] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.RADIO_CONTROL] = (CANDataType.UNSIGNED, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.RADIO_ACKNOWLEDGE] = (CANDataType.UNSIGNED, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.SD_ENABLE_LOGGING] = (CANDataType.UNSIGNED, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.LOGGING_ACKNOWLEDGE] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.LSM_ACC_X] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.LSM_ACC_Y] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.LSM_ACC_Z] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.ADXL_ACC_X] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.ADXL_ACC_Y] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.ADXL_ACC_Z] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.ICM_ACC_X] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.ICM_ACC_Y] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.ICM_ACC_Z] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.LSM_MAGN_FIELD_X] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.LSM_MAGN_FIELD_Y] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.LSM_MAGN_FIELD_Z] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.L3G_RATE_X] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.L3G_RATE_Y] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.L3G_RATE_Z] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.FANCY_RATE_X] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.FANCY_RATE_Y] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.FANCY_RATE_Z] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.ICM_RATE_X] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.ICM_RATE_Y] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.ICM_RATE_Z] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.FILTERED_RATE_X] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.FILTERED_RATE_Y] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.FILTERED_RATE_Z] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.TEMPERATURE] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.BAR_TEMPERATURE1] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.BAR_TEMPERATURE2] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.ONE_WIRE_TEMPERATURE] = (CANDataType.UNSIGNED, CANDataType.FLOAT)
CANMsgDataTypes[CANSid.GPS1_LATITUDE] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GPS2_LATITUDE] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GPS1_LONGITUDE] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GPS2_LONGITUDE] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GPS1_ALT_MSL] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GPS2_ALT_MSL] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GPS1_GND_SPEED] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GPS2_GND_SPEED] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GPS1_FIX_QUAL] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GPS2_FIX_QUAL] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GPS1_DATE_TIME] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GPS2_DATE_TIME] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GPS1_NB_SAT] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GPS2_NB_SAT] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GPS1_TRACK_ANG] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GPS2_TRACK_ANG] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GPS1_MAGN_VAR_TRACK] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GPS2_MAGN_VAR] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MOTOR_WATCHDOG_TIME_LEFT] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MOTOR_DISCONNECT_FUELING] = (CANDataType.MAGIC, CANDataType.NONE)
CANMsgDataTypes[CANSid.MOTOR_OVERRIDE_DISCONNECTION_PROTECTION] = (CANDataType.UNSIGNED, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.MOTOR_SET_FUELING_LOCK] = (CANDataType.UNSIGNED, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.STATUS_LATCH_RESET] = (CANDataType.UNSIGNED, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.PUM_3V3_CURRENT] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.PUM_5V_CURRENT] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.PUM_BAT1_CURRENT] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.PUM_BAT2_CURRENT] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.PUM_BAT3_CURRENT] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.PUM_VBAT1] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.PUM_VBAT2] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.PUM_VBAT3] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.PUM_45V_CHARGED] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.RPM_VOLTAGE] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.RPM_CURRENT] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.RPM_45V] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.RADIO_STATS] = (CANDataType.UNSIGNED, CANDataType.UNSIGNED)
CANMsgDataTypes[CANSid.ERR_CAN_GOT_BAD_MAGIC_BYTES] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.ERR_CAN_SWITCHING_BUS] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.CALIB_SENSOR] = (CANDataType.UNSIGNED, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.LVDM_CHARGED] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MPU_ACC_X] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MPU_ACC_Y] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MPU_ACC_Z] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MPU_RATE_X] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MPU_RATE_Y] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MPU_RATE_Z] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MPU_MAGN_FIELD_X] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MPU_MAGN_FIELD_Y] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MPU_MAGN_FIELD_Z] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.SL_ALTITUDE] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MODULE_BASE_INIT_SUCCESS] = (CANDataType.TIMESTAMP, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.MODULE_SPECIFIC_INIT_SUCCESS] = (CANDataType.TIMESTAMP, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.MODULE_SPECIFIC_INIT_RECOVERABLE_ERROR] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MODULE_SPECIFIC_INIT_FAILURE] = (CANDataType.TIMESTAMP, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.MODULE_HEARTBEAT] = (CANDataType.TIMESTAMP, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.MODULE_GET_STATUS] = (CANDataType.MAGIC, CANDataType.NONE)
CANMsgDataTypes[CANSid.SD_CARD_WRITE_ERROR] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GS_UART_WRITE_ERROR] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.GS_UART_READ_ERROR] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.ADIRM_DATA_QUEUE_FULL] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.SD_CARD_SPACE_LEFT] = (CANDataType.INT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.SD_TOTAL_BYTES_WRITTEN] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.SENSOR_CALIB_X] = (CANDataType.FLOAT, CANDataType.UNSIGNED)
CANMsgDataTypes[CANSid.SENSOR_CALIB_Y] = (CANDataType.FLOAT, CANDataType.UNSIGNED)
CANMsgDataTypes[CANSid.SENSOR_CALIB_Z] = (CANDataType.FLOAT, CANDataType.UNSIGNED)
CANMsgDataTypes[CANSid.MODULE_POS] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.MODULE_NB] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.COMMAND_REQ_MOD_POS_NB] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.CAN_TEST_INT_MAGIC] = (CANDataType.INT, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.CAN_TEST_INT_TIMESTAMP] = (CANDataType.INT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.CAN_TEST_INT_INT] = (CANDataType.INT, CANDataType.INT)
CANMsgDataTypes[CANSid.CAN_TEST_INT_FLOAT] = (CANDataType.INT, CANDataType.FLOAT)
CANMsgDataTypes[CANSid.CAN_TEST_INT_UNSIGNED] = (CANDataType.INT, CANDataType.UNSIGNED)
CANMsgDataTypes[CANSid.CAN_TEST_FLOAT_MAGIC] = (CANDataType.FLOAT, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.CAN_TEST_FLOAT_TIMESTAMP] = (CANDataType.FLOAT, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.CAN_TEST_FLOAT_INT] = (CANDataType.FLOAT, CANDataType.INT)
CANMsgDataTypes[CANSid.CAN_TEST_FLOAT_FLOAT] = (CANDataType.FLOAT, CANDataType.FLOAT)
CANMsgDataTypes[CANSid.CAN_TEST_FLOAT_UNSIGNED] = (CANDataType.FLOAT, CANDataType.UNSIGNED)
CANMsgDataTypes[CANSid.CAN_TEST_UNSIGNED_MAGIC] = (CANDataType.UNSIGNED, CANDataType.MAGIC)
CANMsgDataTypes[CANSid.CAN_TEST_UNSIGNED_TIMESTAMP] = (CANDataType.UNSIGNED, CANDataType.TIMESTAMP)
CANMsgDataTypes[CANSid.CAN_TEST_UNSIGNED_INT] = (CANDataType.UNSIGNED, CANDataType.INT)
CANMsgDataTypes[CANSid.CAN_TEST_UNSIGNED_FLOAT] = (CANDataType.UNSIGNED, CANDataType.FLOAT)
CANMsgDataTypes[CANSid.CAN_TEST_UNSIGNED_UNSIGNED] = (CANDataType.UNSIGNED, CANDataType.UNSIGNED)
CANMsgDataTypes[CANSid.CAN_TEST_MAGIC_NONE] = (CANDataType.MAGIC, CANDataType.NONE)
CANMsgDataTypes[CANSid.CAN_TEST_TIMESTAMP_MAGIC] = (CANDataType.TIMESTAMP, CANDataType.MAGIC)
