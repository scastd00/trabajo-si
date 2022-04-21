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
	return Binary.fraction_to_string(num, ndigits=precision, simplify=False).replace("0.", "")

def binstr_to_fraction(binary: str) -> Fraction:
	"""
	Converts a binary string representation into a Fraction.

	:param binary: binary representation of a number.
	:return: Fraction obtained from the binary representation of a number.
	"""
	return binstr_to_binary(binary).fraction

def binstr_to_binary(binary: str) -> Binary:
	return Binary(binary)

def _r(bin1: str, bin2: str) -> int:
	len1 = len(bin1)
	len2 = len(bin2)
	pos = -1

	for i in range(min(len1, len2)):
		if bin1[i] != bin2[i]:
			pos = i - 1
			break

	if pos == -1:
		# Todo: handle special case
		print("Special")

	return pos

def obtain_number_inside_interval(low: str, high: str) -> str:
	r = _r(low, high)
	result: str

	if len(high) > r + 2:
		result = high[0:r + 2]  # r starts at 0, so r+1 => r+2
	else:
		# Todo: handle this case
		result = ""

	return "0." + result

def print_float(value: float):
	print(f'{value:.30f}')

def execute(block: List[str]):
	text = block[0].replace("\n", "  ")
	probabilities = build_alphabet_with_probabilities(text)
	intervals_from_probabilities(probabilities)

	encoded = encode(text, probabilities)
	high_str, low_str = interval_binary_representation(encoded)

	print(str(low_str))
	print(str(high_str))
	print(low_str == high_str)

	num = obtain_number_inside_interval(low_str, high_str)

	# print_float(binstr_to_fraction("0." + num).__float__())

	print(binstr_to_binary("0." + low_str))
	print(binstr_to_binary(num))
	print(binstr_to_binary("0." + high_str))

	# _r = r(low_str, high_str)
	# print(low_str[_r], low_str[_r+1])
	# print(high_str[_r], high_str[_r+1])

	num = encoded.get_low()  # Todo: remove this line

	decoded = decode(
		probabilities,
		num,
		# binstr_to_fraction(num),
		len(text)
	)

	new_line = '\n'
	print(f"Decoded string:\n\n{decoded.replace('  ', new_line)}\n")

	# pruebas_casos()
	print(num)

# print(low)
# print(high)
# print(low == high)

def pruebas_casos():
	print("Caso 1")
	print("Normal")
	# print(TwosComplement("0.01000101000").to_float(), "No vale")  # Es más pequeño
	print("Low: ", TwosComplement("0.0100010100011011101110011001100111101010").to_float())
	print("     ", TwosComplement("0.0100010101").to_float())  # Truncar el mayor
	print("High:", TwosComplement("0.0100010101100000010000011000100100110111").to_float())
	# print(TwosComplement("0.01000101100").to_float(), "No vale")  # Es más grande
	print("Otro\n")
	# Todo: Cuidado al truncar, que si me quedan muchos ceros, me puede quedar más pequeño que el menor
	print("Caso 2")
	print("Normal")
	print("Low: ", TwosComplement("0.0100010100011011101110011001100111101010").to_float())
	print("     ", TwosComplement("0.01000101000111").to_float())  # Sumar 1 a l_r+1
	print("High:", TwosComplement("0.0100010101100000010000011000100100110111").to_float())
	print("Otro\n")
	# Notas que no sé si servirán
	# Si cuando coinciden, lo hacen en 1, al sumar es 0, pero se arrastra 1 a la posición anterior
	#
	# print("Caso Especial")
	# print("Normal")
	# print("Low: ", TwosComplement("0.0100010100111011101110011001000111101010").to_float())
	# print("     ", TwosComplement("0.010001010011101110111001100101").to_float())  # Sumar 1 a l_r+1
	# print("High:", TwosComplement("0.0100010100111011101110011001100111101010").to_float())
	# print("Otro\n")
	print()

def interval_binary_representation(encoded: Interval) -> [str, str]:
	"""
	Calculates the interval values in binary representation. The precision is
	incremented until the representations are different.

	Precision starts at 100 and doubles its value each iteration.

	:param encoded: Interval to calculate the binary representation.
	:return: Binary representation of the interval *decimal* values (both different).
			 The integer part of the interval is removed
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

if __name__ == '__main__':
	run("./datos_3.txt")
