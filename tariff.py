import pandas as pd
import datetime

tariffs_csv = "tariffs_csv.csv"

class comm_tariff:
	def __init__(self, name):
		self.name = name
		tariff_info = load_tariff_info(name)
		for i in range(1,3):
			intermediate = datetime.datetime.strptime(tariff_info[i], "%m/%d/%y").date()
			tariff_info[i] = datetime.datetime(intermediate.year, intermediate.month, intermediate.day, 0, 0)

		self.seasons = {'Winter Start': tariff_info[1], 
						'Summer Start': tariff_info[2]
						}
		# for i in range(3, 14):
		# 	if tariff_info[i] == '$-':
		# 		tariff_info[i] = 0
		# 	else:
		# 		tariff_info[i] = float(tariff_info[i][1:])
		for j in range(3, 14):
			tariff_info[j] = float(tariff_info[j])
		self.rates = {'Max kW Peak (summer)': tariff_info[3], 'Part kW Peak (summer)': tariff_info[4], 
			'Part kW Peak (winter)': tariff_info[5], 'Anytime kW Peak (summer)': tariff_info[6], 
			'Anytime kW Peak (winter)': tariff_info[7], 
			'kWh Peak (summer)': tariff_info[8], 'kWh Peak (winter)': tariff_info[9], 
			'kWh Part Peak (summer)': tariff_info[10], 'kWh Part Peak (winter)': tariff_info[11],
			'kWh Off Peak (summer)': tariff_info[12], 'kWh Off Peak (winter)': tariff_info[13]
			}
		self.hours = {
			'Off Peak Morning Start (summer)': tariff_info[14], 'Off Peak Evening End (summer)': tariff_info[15],
			'Park Peak Morning Start (summer)': tariff_info[16],'Part Peak Morning End (summer)': tariff_info[17],
			'Park Peak Evening Start (summer)': tariff_info[18], 'Part Peak Evening End (summer)': tariff_info[19],
			'Peak Start (summer)': tariff_info[20], 'Peak End (summer)': tariff_info[21],
			'Off Peak Morning Start (winter)': tariff_info[22],'Off Peak Evening End (winter)': tariff_info[23],
			'Park Peak Morning Start (winter)': tariff_info[24], 'Part Peak Morning End (winter)': tariff_info[25],
			'Park Peak Evening Start (winter)': tariff_info[26], 'Part Peak Evening End (winter)': tariff_info[27],
			'Peak Start (winter)': tariff_info[28], 'Peak End (winter)': tariff_info[29]
			}

def load_tariff_info(name):
	tariff_list = []
	df = pd.read_csv(tariffs_csv)
	for index, row in df.iterrows():
		tariff_list.append(row[name])
	return tariff_list
	