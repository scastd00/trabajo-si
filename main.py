import re
from fractions import Fraction
from math import log2
from typing import Dict, List

from binary_fractions import Binary, TwosComplement

from Interval import Interval
from Item import Item

def num_n_decode(num: Fraction, lj: Fraction, hj: Fraction) -> Fraction:
	"""
	Determines the new number to be decoded.

	:param num: number to decode.
	:param lj: lower part of the interval
	:param hj: higher part of the interval.
	:return:
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

	:param data: table to calculate entropy
	:return: entropy of the code
	"""
	result = Fraction(0)

	for k, v in data.items():
		p_i = v.get_probability()
		result += p_i * log2(1 / p_i)

	return result

def determine_decode_interval_of(num: Fraction, interval_dict: Dict[str, Item]) -> str:
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

def build_alphabet_with_probabilities(text: str) -> Dict[str, Item]:
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
	valid_blocks = read_file(file)
	execute(valid_blocks[0])

def read_file(file: str) -> List[List[str]]:
	"""
	Reads a file and returns a list containing each of the parts in it.
	File structure is as follows:

	Ejercicio <number>

	Content (text to be encoded)

	número decimal=<number>
	EOF

	:param file: file to read.
	:return: List with each part of the file.
	"""
	file = open(file)
	all_lines = file.read()
	split_on_exercise = re.split("Ejercicio .\n\n", all_lines)
	valid_blocks = []

	for text in split_on_exercise:
		if len(text) != 0:
			valid_blocks.append(text.split("\n\n")[0:2])

	file.close()
	del all_lines
	del split_on_exercise
	return valid_blocks

def decode(all_values: Dict[str, Item], number: Fraction, iterations: int) -> str:
	"""
	Performs the arithmetic decoding of the number.

	:param all_values: code dictionary with the intervals.
	:param number: number to decode.
	:param iterations: number of iterations to perform.
	:return: decoded string.
	"""
	auxStr = ""

	for i in range(iterations):
		s = determine_decode_interval_of(number, all_values)
		auxStr += s
		interval = all_values[s].get_interval()
		number = num_n_decode(number, interval.get_low(), interval.get_high())

	return auxStr

def encode(text: str, data: Dict[str, Item]) -> Interval:
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
	:return:
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

	# Todo: soportar que si la precisión hace que sean iguales high y low,
	#  volver a calcular los dígitos binarios con una precisión mayor.
	return Interval(low, high)

def get_decimal_digits(num: Fraction, precision: int = 500) -> str:
	"""
	Determines the binary representation of the Fraction and takes only the decimal
	digits, since the number is always between 0 and 1.

	:param num: Number to represent in binary.
	:param precision: number of decimal digits to calculate.
	:return: string of binary representation of the decimal part of the Fraction.
	"""
	return Binary.fraction_to_string(num, ndigits=precision, simplify=False).replace("0.", "")

def obtain_number_inside_interval(low: str, high: str) -> str:
	new_high = high.ljust(len(low), '0')

	defer = 0
	for i in range(len(low)):
		if low[i] != new_high[i]:
			defer = i
			break

	return ""

def execute(block: List[str]):
	text = block[0].replace("\n", "  ")
	probabilities = build_alphabet_with_probabilities(text)
	intervals_from_probabilities(probabilities)

	encoded = encode(text, probabilities)
	decoded = decode(probabilities, encoded.get_low(), len(text))
	new_line = '\n'
	print(f"Decoded string:\n\n{decoded.replace('  ', new_line)}\n")

	low = get_decimal_digits(encoded.get_low(), 2000)
	high = get_decimal_digits(encoded.get_high(), 2000)
	# low = get_decimal_digits(Fraction("0.2699543"), 40)
	# high = get_decimal_digits(Fraction("0.271"), 40)

	print("Caso 1")
	print("Normal")
	# print(TwosComplement("0.01000101000").to_float(), "No vale")  # Es más pequeño
	print(TwosComplement("0.0100010100011011101110011001100111101010").to_float())
	print(TwosComplement("0.0100010101").to_float()) # Truncar el mayor
	print(TwosComplement("0.0100010101100000010000011000100100110111").to_float())
	# print(TwosComplement("0.01000101100").to_float(), "No vale")  # Es más grande
	print("Otro\n")

	# Todo: Cuidado al truncar, que si me quedan muchos ceros, me puede quedar más pequeño que el menor

	print("Caso 2.1")
	print("Normal")
	print(TwosComplement("0.0100010100011011101110011001100111101010").to_float())
	print(TwosComplement("0.01000101001").to_float())  # Sumar 1 a l_r+1
	print(TwosComplement("0.0100010101100000010000011000100100110111").to_float())
	print("Otro\n")

	print("Caso 2.2")
	print("Normal")
	print(TwosComplement("0.0100010100011011101110011001100111101010").to_float())
	print(TwosComplement("0.01000101000111").to_float())  # Sumar 1 a última cifra donde cambia
	print(TwosComplement("0.0100010101100000010000011000100100110111").to_float())
	print("Otro\n")

	print()
	num = obtain_number_inside_interval(low, high)

	print(low)
	print(high)
	print(low == high)

if __name__ == '__main__':
	run("./datos_3.txt")
