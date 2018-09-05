"""Units.py
	Conversion d'altitude et d'unités

Auteur:
	Adrien Lessard, Youva Chemam

Copyright 2018. Oronos Polytechnique. Tous droits réservés
"""


class Units:

	M_TO_FT = 3.28084
	FT_TO_M = 1.0 / M_TO_FT

	@staticmethod
	def pascalToMeters(press_pa: float) -> float:
		return (1.0 - (press_pa / 101325) ** 0.19026323) * 44330.77

	@staticmethod
	def pascalToFeet(press_pa: float) -> float:
		return Units.pascalToMeters(press_pa) * Units.M_TO_FT

	@staticmethod
	def toSigned(x: int) -> int:
		""" Convert unsigned to signed """
		return -1 * ((x ^ 0xFFFFFFFF) + 1) if (x >> 31) == 1 else x
