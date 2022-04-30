from typing import List

SPACE = ' '
NEW_LINE = SPACE + SPACE
EOF = ''

class Reader:
	"""
	Class for reading the problem file.
	"""

	def __init__(self, file_path: str, step: int = 1):
		"""
		Initializes the Reader.

		:param file_path: path to the file to read.
		:param step: number of characters to read in one read operation.
		"""
		self.reader = open(file_path, 'r')
		self.step = step

	def read(self) -> List[str]:
		"""
		Reads the complete file using the step specified in the constructor.

		:return: List with all the characters read.
		"""
		builder = ""

		for buffer in iter(lambda: self.reader.read(1), EOF):
			if buffer == '\r':
				continue

			if buffer == '\n':
				builder += NEW_LINE
			elif buffer == ' ':
				builder += SPACE
			else:
				builder += buffer

		builder = builder.rstrip(SPACE)  # Remove trailing space characters.

		return [builder[i:i + self.step] for i in range(0, len(builder), self.step)]
