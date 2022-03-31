from fractions import Fraction

class Interval:
	def __init__(self, low = Fraction(0), high = Fraction(1)):
		self.low = low
		self.high = high

	def get_low(self):
		return self.low

	def get_high(self):
		return self.high

	def __str__(self):
		return '{0} {1}'.format(self.low.__float__(), self.high.__float__())