from fractions import Fraction
from decimal import Decimal, Context

class Interval:
	def __init__(self, low = Fraction(0), high = Fraction(1)):
		self.low = low
		self.high = high

	def get_low(self) -> Fraction:
		return self.low

	def get_low_decimal(self) -> Decimal:
		return Decimal(self.low.numerator / self.low.denominator, Context(prec=1000))

	def get_high(self) -> Fraction:
		return self.high

	def get_high_decimal(self) -> Decimal:
		return Decimal(self.high.numerator / self.high.denominator, Context(prec=1000))

	def __str__(self):
		return '[{0}, {1}]'.format(self.low.__float__(), self.high.__float__())