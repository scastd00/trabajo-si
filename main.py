import math
from fractions import Fraction
from typing import Dict, List
from time import time

from binary_fractions import Binary

from ExportCSV import ExportCSV
from Interval import Interval
from Item import Item
from Reader import Reader

debug = 0
BITS_IN_ASCII = 8
SEPARATOR = 'X'
NEW_LINE = '\n'

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

def build_alphabet_with_probabilities(text_blocks: List[str]) -> Dict[str, Item]:
	"""
	Creates a dictionary with the letters of the text mapped with an Item, containing
	the probability, frequency and the interval of it.
	If a letter is not in the dictionary, the entry is created with the default value.

	:param text_blocks: text to map.

	:return: Dict containing the letters of the text mapped.
	"""
	alphabet: Dict[str, Item] = {}
	val = Fraction(1, len(text_blocks))  # Default value

	for char in text_blocks:
		try:
			alphabet[char].add_probability(val)
			alphabet[char].increment_frequency()
		except KeyError:
			alphabet[char] = Item(val)  # Entry is created in alphabet

	return alphabet

def add_intervals_to_probs(probabilities: Dict[str, Item]):
	"""
	Calculates the intervals (higher and lower parts) of each item in the dictionary.

	:param probabilities: code table of probabilities.

	:return: the same dictionary with the intervals of each item added to it.
	"""
	lo = Fraction(0)

	for letter, item in probabilities.items():
		prob = item.get_probability()
		item.set_interval(Interval(lo, lo + prob))
		lo += prob

def calculate_ratio(length: int, base_ratio: int) -> float:
	"""
	Calculates the ratio comparing the length of the text to the base ratio.

	:param length: length of the encoded text.
	:param base_ratio: base ratio of the text.
	:return: ratio of the text.
	"""
	return Fraction(length, base_ratio, _normalize=False).__float__()

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
	return Reader(file, step).read()

def decode(probabilities: Dict[str, Item], number: Fraction, iterations: int) -> str:
	"""
	Performs the arithmetic decoding of the number.

	:param probabilities: code dictionary with the intervals.
	:param number: number to decode.
	:param iterations: number of iterations to perform.

	:return: decoded string.
	"""
	if debug:
		print(f'Initial number: {number.__float__()}')

	decoded_str = ""
	num_to_decode = number

	for i in range(iterations):
		decoded_letter = determine_letter_of(num_to_decode, probabilities)
		decoded_str += decoded_letter
		interval = probabilities[decoded_letter].get_interval()

		if debug:
			print(f'Num: {format_float(num_to_decode.__float__(), 5)} inside of '
				  f'[{format_float(interval.get_low().__float__(), 5)}, {format_float(interval.get_high().__float__(), 5)})'
				  f' -> letter: {decoded_letter}')

		num_to_decode = num_n_decode(num_to_decode, interval.get_low(), interval.get_high())

	return decoded_str

def encode(text: str, probs: Dict[str, Item]) -> Interval:
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
	:param probs: code dictionary with the intervals.

	:return: the interval in which the number resulting from the encoding is.
	"""
	low = Fraction(0)
	high = Fraction(1)

	for char in text:
		value = probs[char]
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

	:param binary: binary representation of a number. IMPORTANT: the binary string must be like '0.decimals'

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
	return '0' if number == '1' else '1'

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

def divisorsOf(num: int, minimum: int = 0) -> List[int]:
	divisors = []

	for i in range(1, math.ceil(num / 2) + 1):
		if num % i == 0 and i >= minimum:
			divisors.append(i)

	print(f"Divisors of {num}: {divisors}")
	return divisors

def run(file_name: str):
	file_content = read_file(file_name)
	file_content_length = len(file_content)
	divisors = divisorsOf(file_content_length)  # Todo: Change second parameter to something more reasonable
	# print(divisors)
	#
	# return

	# Each character is mapped a probability for all execution
	probabilities_by_letter = build_alphabet_with_probabilities(file_content)
	add_intervals_to_probs(probabilities_by_letter)
	export_list = [
		[
			'Longitud de bloque',
			'Longitud cadena codif. Binaria',
			'Longitud cadena codif. ASCII',
			'Ratio',
			'Tiempo de ejecución (seg)'
		]
	]

	for block_divisor in divisors:
		print(f"DIVISOR: {block_divisor}")
		file_blocks = read_file(file_name, block_divisor)
		encoded_blocks = []
		encoded_length = 0

		start_time = time()  # Start timer

		for block in file_blocks:
			encoded_block = encode_block(block, probabilities_by_letter)
			encoded_blocks.append(encoded_block)
			encoded_length += len(encoded_block)

		end_time = time()  # End timer

		encoded_text = SEPARATOR.join(encoded_blocks)

		print(f'Execution time {format_float(end_time - start_time, 6)} seconds')
		# print(f'Encoded blocks: {encoded_blocks}')
		# print(f'Raw blocks: {file_blocks}')
		# print(f'Encoded text: {encoded_text}')
		ratio = calculate_ratio(encoded_length, file_content_length * BITS_IN_ASCII)
		print(f'Ratio: {ratio} == {encoded_length} / {file_content_length * BITS_IN_ASCII}')

		# decoded = decode_text_with_separator(encoded_text, SEPARATOR, probabilities_by_letter, block_divisor)
		# print(f'Decoded text: {decoded.replace("  ", NEW_LINE)}')
		# print('\n')
		export_list.append([str(block_divisor), str(encoded_length), str(file_content_length * BITS_IN_ASCII), str(format_float(ratio, 6)), format_float(end_time - start_time, 6)])

	exporter = ExportCSV(file_name + "_Exported.csv")
	exporter.export(export_list)

def decode_text_with_separator(
		text: str, separator: str, probabilities: Dict[str, Item], iterations: int
) -> str:
	"""
	Decodes a text with a separator.

	:param text: Text to decode.
	:param separator: Separator to use.
	:param probabilities: Probabilities of each character.
	:param iterations: Number of iterations to perform.

	:return: Decoded text.
	"""
	decoded_text = ''
	blocks = text.split(separator)
	for block in blocks:
		decoded_text += decode(probabilities, binstr_to_fraction("0." + block), iterations)

	return decoded_text

def encode_block(block: str, probs: Dict[str, Item]) -> str:
	"""
	:param block: Block to encode. Example: 'Python e'
	:param probs: Probabilities of each character
	:return: Encoded block
	"""
	encoded_block = encode(block, probs)
	high_str, low_str = interval_binary_representation(encoded_block)
	num_decimal_part = obtain_decimal_part_of_number_inside_interval(low_str, high_str)

	if debug:
		print("Low :", "0." + low_str)
		print("Num :", "0." + num_decimal_part)
		print("High:", "0." + high_str)

	return num_decimal_part

if __name__ == '__main__':
	run("datos_1800_2")
