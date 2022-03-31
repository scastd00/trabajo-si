import re
from fractions import Fraction
from math import log2
from typing import Dict, List

from Interval import Interval
from Item import Item

from bigfloat import BigFloat
from bigfloat import Context

def num_n_decode(num: Fraction, lj: Fraction, hj: Fraction) -> Fraction:
	return (num - lj) / (hj - lj)

def x_n_encode(x: Fraction, L: Fraction, H: Fraction, L_n_: Fraction, H_n_: Fraction) -> Fraction:
	return (((x - L) * (H_n_ - L_n_)) / (H - L)) + L_n_

def L_n(L: Fraction, H: Fraction, L_j: Fraction) -> Fraction:
	return L + ((H - L) * L_j)

def H_n(L: Fraction, H: Fraction, H_j: Fraction) -> Fraction:
	return L + ((H - L) * H_j)

def entropy(data: Dict[str, Item]) -> Fraction:
	result = Fraction(0)

	for key, value in data.items():
		p_i = value.get_probability()
		result += p_i * log2(1 / p_i)

	return result

def get_total_frequency(mappings: Dict[str, Item]) -> int:
	return sum(mappings.values())

def determine_decode_interval_of(num: Fraction, interval_dict: Dict[str, Item]) -> str:
	interval_key = ""

	for key, value in interval_dict.items():
		if value.get_low_interval() <= num < value.get_high_interval():
			interval_key = key
			break

	return interval_key

def build_alphabet_with_probabilities(text: str) -> Dict[str, Item]:
	alphabet: Dict[str, Item] = {}
	val = Fraction(1, len(text))

	for char in text:
		try:
			alphabet[char].add_probability(val)
			alphabet[char].increment_frequency()
		except KeyError:
			alphabet[char] = Item(val)

	return alphabet

def intervals_from_probabilities(probabilities: Dict[str, Item]):
	lo = Fraction(0)

	for letter, item in probabilities.items():
		frac = item.get_probability()
		item.set_interval(Interval(lo, lo + frac))
		lo += frac

def run(file: str):
	valid_blocks = read_file(file)

	parse_block_and_execute(valid_blocks[0], 27)
	extra(valid_blocks[0])

# parse_block_and_execute(valid_blocks[1], 19)
# parse_block_and_execute(valid_blocks[2], 17)
# parse_block_and_execute(valid_blocks[3], 27)

def read_file(file: str) -> List[List[str]]:
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
	auxStr = ""

	for i in range(iterations):
		s = determine_decode_interval_of(number, all_values)
		auxStr += s
		interval = all_values.get(s).get_interval()
		number = num_n_decode(number, interval.get_low(), interval.get_high())

	return auxStr

def parse_block_and_execute(block: List[str], code_length: int):
	text = block[0].replace("\n", "  ")
	decimal_number = block[1].split("=")[1]

	probabilities = build_alphabet_with_probabilities(text)
	intervals_from_probabilities(probabilities)

	num = Fraction(decimal_number)
	decoded = decode(probabilities, num, code_length)
	print(f"Cadena: {decoded} -> Entropy:", entropy(probabilities))

def get_interval_from_letter(letter: str, code: Dict[str, Item]) -> Interval:
	return code.get(letter).get_interval()

def encode_text(text: str, data: Dict[str, Item]) -> List[Fraction]:
	low = Fraction(0)
	high = Fraction(1)

	for char in text:
		value = data[char]
		L_j = value.get_low_interval()
		H_j = value.get_high_interval()
		low = L_n(low, high, L_j)  # Update value
		high = H_n(low, high, H_j)  # Update value

	# Todo: saber en qué número difieren y coger hasta ahí
	#  Pasar números a binario e ir comparando posiciones
	return [low, high]

def get_binary_representation(num: Fraction) -> str:
	return bin((num * num.denominator).numerator).replace("0b", "", 1)

def format_double(prob: Fraction):
	print(BigFloat.exact((prob * prob.denominator).numerator.__str__(), precision=30000))
	return '{0:.700f}'.format(prob.__float__())

def extra(block: List[str]):
	text = block[0].replace("\n", "  ")
	decimal_number = block[1].split("=")[1]
	probabilities = build_alphabet_with_probabilities(text)
	intervals_from_probabilities(probabilities)

	encoded = encode_text(text, probabilities)
	print(
		# f'Low: {get_binary_representation(encoded[0])}\n'
		# f'High: {get_binary_representation(encoded[1])}\n'
		f'Algo : {format_double(encoded[1])}\n'
	)

if __name__ == '__main__':
	run("./datos_3.txt")

# Explica con un ejemplo cómo puede ir el proceso de intercalado
