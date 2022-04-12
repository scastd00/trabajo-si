from fractions import Fraction

from Interval import Interval

class Item:
	def __init__(self, probability: Fraction, frequency: int = 1):
		self.probability: Fraction = probability
		self.frequency: int = frequency
		self.interval: Interval = Interval()

	def get_probability(self) -> Fraction:
		return self.probability

	def get_frequency(self) -> int:
		return self.frequency

	def add_probability(self, prob):
		self.probability += prob

	def increment_frequency(self):
		self.frequency += 1

	def get_interval(self) -> Interval:
		return self.interval

	def set_interval(self, interval: Interval):
		self.interval = interval

	def get_low_interval(self) -> Fraction:
		return self.interval.get_low()

	def get_high_interval(self) -> Fraction:
		return self.interval.get_high()

	def __add__(self, other):
		return self.probability + other.get_probability()
