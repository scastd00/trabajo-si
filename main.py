import math
from fractions import Fraction
from math import log2
from typing import Dict, List

from binary_fractions import Binary

from Interval import Interval
from Item import Item
from Reader import Reader

debug = 0

def num_n_decode(num: Fraction, lj: Fraction, hj: Fraction) -> Fraction:
	"""
	Determines the new number to be decoded.

	:param num: number to decode.
	:param lj: lower part of the interval
	:param hj: higher part of the interval.

	:return: number mapped to [0, 1)
	"""
	return (num - lj) / (hj - lj)

def L_n(L: Fraction, H: Fraction, L_j: Fraction) -> Fraction:
	"""
	Calculates the new lower interval part.

	:param L: current lower interval value.
	:param H: current higher interval value.
	:param L_j: lower part of the interval (between 0 and 1) of the letter.

	:return: new lower interval part.
	"""
	return L + ((H - L) * L_j)

def H_n(L: Fraction, H: Fraction, H_j: Fraction) -> Fraction:
	"""
	Calculates the new higher interval part.

	:param L: current lower interval value.
	:param H: current higher interval value.
	:param H_j: higher part of the interval (between 0 and 1) of the letter.

	:return: new higher interval part.
	"""
	return L + ((H - L) * H_j)

def entropy(data: Dict[str, Item]) -> Fraction:
	"""
	Calculates the entropy of the code.
	Formula used:
			   m
		H(F) = Σ p_i * log2(1 / p_i)
			  i=1

	:param data: table to calculate entropy.

	:return: entropy of the code.
	"""
	result = Fraction(0)

	for k, v in data.items():
		p_i = v.get_probability()
		result += p_i * log2(1 / p_i)

	return result

def determine_letter_of(num: Fraction, interval_dict: Dict[str, Item]) -> str:
	"""
	Determines the letter of the interval in which the given number is in the code table.

	:param num: number to search the interval for.
	:param interval_dict: code table containing all the intervals of the code.

	:return: the letter of the interval in which the given number is.
	"""
	interval_key = ""

	for k, v in interval_dict.items():
		if v.get_low_interval() <= num < v.get_high_interval():
			interval_key = k
			break

	return interval_key

def build_alphabet_with_probabilities(text: List[str]) -> Dict[str, Item]:
	"""
	Creates a dictionary with the letters of the text mapped with an Item, containing
	the probability, frequency and the interval of it.
	If a letter is not in the dictionary, the entry is created with the default value.

	:param text: text to map.

	:return: Dict containing the letters of the text mapped.
	"""
	alphabet: Dict[str, Item] = {}
	val = Fraction(1, len(text))

	for char in text:
		try:
			alphabet[char].add_probability(val)
			alphabet[char].increment_frequency()
		except KeyError:
			alphabet[char] = Item(val)  # Entry is created in alphabet

	return alphabet

def intervals_from_probabilities(probabilities: Dict[str, Item]):
	"""
	Calculates the intervals (higher and lower parts) of each item in the dictionary.

	:param probabilities: code table of probabilities.

	:return: the same dictionary with the intervals of each item added to it.
	"""
	lo = Fraction(0)

	for letter, item in probabilities.items():
		frac = item.get_probability()
		item.set_interval(Interval(lo, lo + frac))
		lo += frac

def run(file: str):
	length = len(read_file(file))
	divisors = divisorsOf(length)

	encodedLengths = []

	for i in divisors:
		print(f"DIVISOR: {i}")
		valid_blocks = read_file(file, i)
		encodedLengths.append(execute(valid_blocks))

	calculateRatios(encodedLengths)

def calculateRatios(lengths: List[int]):
	for length in lengths:
		calc = lengths[0] / length
		print(length, ':', lengths[0], calc)
		print(f'1 character every {math.floor(calc)}')

def read_file(file: str, step: int = 1) -> List[str]:
	"""
	Reads a file and returns a list containing each of the parts in it.
	File structure is as follows:

	Content (text to be encoded)
	EOF

	:param file: file to read.
	:param step: step when reading the file.

	:return: List with each part of the file.
	"""
	reader = Reader(file, step)
	return reader.read()

def decode(all_values: Dict[str, Item], number: Fraction, iterations: int) -> str:
	"""
	Performs the arithmetic decoding of the number.

	:param all_values: code dictionary with the intervals.
	:param number: number to decode.
	:param iterations: number of iterations to perform.

	:return: decoded string.
	"""
	auxStr = ""
	if debug:
		print(f'Initial number: {number.__float__()}')

	for i in range(iterations):
		s = determine_letter_of(number, all_values)
		auxStr += s
		interval = all_values[s].get_interval()
		if debug:
			print(f'Num: {format_float(number.__float__(), 5)} inside of '
				  f'[{format_float(interval.get_low().__float__(), 5)}, {format_float(interval.get_high().__float__(), 5)})'
				  f' -> letter: {s}')

		number = num_n_decode(number, interval.get_low(), interval.get_high())

	return auxStr

def encode(text: List[str], data: Dict[str, Item]) -> Interval:
	"""
	Performs the arithmetic encoding of the given text.

	low                                              high
	0                        0.5                        1
	[-------------------------|-------------------------)
			  |(new interval)|
	          ^--------------^
	         L_j           H_j

	The new interval is going to be spitted into the same intervals as the previous one.
	It deepens inside the (0, 1) interval adding more decimals to a Fraction.

	:param text: text to encode.
	:param data: code dictionary with the intervals.

	:return: the interval in which the number resulting from the encoding is.
	"""
	low = Fraction(0)
	high = Fraction(1)

	for char in text:
		value = data[char]
		# Get the interval of a character between 0 and 1.
		L_j = value.get_low_interval()
		H_j = value.get_high_interval()
		# Map the new interval to fit in the [ L_j, H_j ) interval
		L_new = L_n(low, high, L_j)
		H_new = H_n(low, high, H_j)
		low = L_new
		high = H_new

	return Interval(low, high)

def get_decimal_digits(num: Fraction, precision: int = 500) -> str:
	"""
	Determines the binary representation of the Fraction and takes only the decimal
	digits, since the number is always between 0 and 1.

	:param num: Number to represent in binary.
	:param precision: number of decimal digits to calculate.

	:return: string of binary representation of the decimal part of the Fraction.
	"""
	return Binary.fraction_to_string(num, precision, simplify=False).replace("0.", "")

def binstr_to_fraction(binary: str) -> Fraction:
	"""
	Converts a binary string representation into a Fraction.

	:param binary: binary representation of a number.

	:return: Fraction obtained from the binary representation of a number.
	"""
	return _binstr_to_binary(binary).fraction

def _binstr_to_binary(binary: str) -> Binary:
	"""
	Creates a binary representation of a binary string number.

	:param binary: binary representation of a number.

	:return: Binary object for the given representation.
	"""
	return Binary(binary)

def _r(bin1: str, bin2: str) -> int:
	"""
	Calculates the position at which the given strings differ from each other.
	Starting from 0.

	:param bin1: first string.
	:param bin2: other string.

	:return: position of the difference.
	"""
	len1 = len(bin1)
	len2 = len(bin2)
	pos = -1

	for i in range(min(len1, len2)):
		if bin1[i] != bin2[i]:
			pos = i - 1
			break

	# if pos == -1:
	# 	pos = -1

	return pos

def add(number: str) -> str:
	"""
	Makes the addition of the number string received + 1 (binary)

	:param number: number to add.

	:return: number + 1 (as string).
	"""
	if number == '1':
		return '0'  # 1 + 1 = 0 (binary)
	else:
		return '1'  # 0 + 1 = 1 (binary)

def obtain_decimal_part_of_number_inside_interval(low: str, high: str) -> str:
	"""
	Calculates the decimal part of a number that is between the given low and high string values.
	There are 2 cases:
		If high has more than r+1 values:
			-> return the first r+1 values from high (Truncate high).

		Otherwise:
			If low[r+1]+1 != high[r+1]:
				-> return first r values of low and the r+1 value + 1 (low[0:r] low[r+1]+1)
			If low[r+1]+1 == high[r+1]: (Else)
				-> return first r+1 values and the next ones until a 0 is found, and it is added 1.

	:param low: low part of the interval.
	:param high: high part of the interval.

	:return: the decimal part of the number that is inside the interval [low, high).
	"""
	r = _r(low, high) + 1  # To include the position
	# IMPORTANT: r = r + 1
	result: str

	if len(high) > r + 1:
		result = high[:r + 1]  # We must include the r+1 position, so (r+1) + 1
	else:
		max_len = max(len(high), len(low))
		low = low.ljust(max_len + 10, '0')
		high = high.ljust(max_len + 10, '0')
		# Esto no es necesario, pero vale para calcular un número que fijo está dentro del intervalo
		# No importa el número de ceros que se añadan al final del string. Solo se añadirá un 1.
		#
		# Ajustamos las longitudes para poner ceros al final de los números
		# Así, si hemos terminado las cifras decimales de low, podemos añadir un 1 más
		# para que el número resultante quede dentro del intervalo. Ver con el texto 'ab'
		# en el fichero.
		# Los números quedarían:
		#	- 0001101100000
		#			  ^^^^^
		#	- 0001110000000
		#           ^^^^^^^
		#	Result:   ^
		#	  000110111 (Last number is calculated in the line with the condition if l == '0')
		#

		if add(low[r]) != high[r]:
			result = low[:r] + add(low[r + 1])
		else:
			result = low[:r + 1]
			for l in low[r + 1:]:
				if l == '0':
					result += '1'
					break
				else:
					result += l

	if debug:
		print(f"Value of r = {r}")

	return result

def print_float(value: float):
	print(format_float(value, 30))

def format_float(value: float, decimal_places: int) -> str:
	return f'{value:.{decimal_places}f}'

def execute(block: List[str]) -> int:
	"""

	:param block:
	:return: the length of the encoded number (only decimal places)
	"""
	# text = block.replace("\n", "  ")
	text = block
	probabilities = build_alphabet_with_probabilities(text)
	intervals_from_probabilities(probabilities)

	print(f"Plain text to encode:\n{text}\n")

	encoded = encode(text, probabilities)
	high_str, low_str = interval_binary_representation(encoded)

	num_decimal_part = obtain_decimal_part_of_number_inside_interval(low_str, high_str)

	if debug:
		print("Low :", "0." + low_str)
		print("Num :", "0." + num_decimal_part)
		print("High:", "0." + high_str)

	decoded = decode(
		probabilities,
		binstr_to_fraction("0." + num_decimal_part),
		len(text)
	)

	new_line = '\n'
	print(f"\nDecoded string:\n{decoded.replace('  ', new_line)}\n")

	return len(num_decimal_part)

def interval_binary_representation(encoded: Interval) -> [str, str]:
	"""
	Calculates the interval values in binary representation. The precision is
	incremented until the representations are different.

	Precision starts at 100 and doubles its value each iteration.

	:param encoded: Interval to calculate the binary representation.

	:return: Binary representation of the interval *decimal* values (both different).
			 The integer part of the interval is removed.
	"""
	precision = 100
	low_str = get_decimal_digits(encoded.get_low(), precision)
	high_str = get_decimal_digits(encoded.get_high(), precision)

	# Compare strings until they differ to make the correct encoding
	while low_str == high_str:
		precision *= 2  # Increase the precision
		low_str = get_decimal_digits(encoded.get_low(), precision)
		high_str = get_decimal_digits(encoded.get_high(), precision)

	return high_str, low_str

def divisorsOf(num: int) -> List[int]:
	divisors = []

	for i in range(1, math.ceil(num / 2) + 1):
		if num % i == 0:
			divisors.append(i)

	print(f"Divisors of {num}: {divisors}")
	return divisors

if __name__ == '__main__':
	run("datos")
