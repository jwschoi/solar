class tariff:
	def __init__(self, name):
		self.name = name
		self.seasons = self.load_seasons(name)


	def load_seasons(self, tariff_name):
		to_return = []
		file = open("seasons.txt", "r")
		for lines in file:
			word = lines.split()
			if word[0] == tariff_name:
				to_return.append(word[1])
				to_return.append(word[2])
		# if to_return is empty, error out
		if not to_return:
			print("No such thing\n")
			return
		return to_return