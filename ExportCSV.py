from typing import List
import csv

class ExportCSV:
	def __init__(self, filename: str):
		self.filename = filename

	def export(self, data: List[List[str]]) -> None:
		with open(self.filename, 'w') as f:
			writer = csv.writer(f)
			writer.writerows(data)
