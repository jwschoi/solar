import requests
import xlwt
import json
import datetime
from datetime import date
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from tariff import comm_tariff
import math
from openpyxl import load_workbook

YEAR = date.today().year
CUST_USE = "Intake.csv"
OUTPUT = "Template.xlsx"
SHEET_TO_PRINT_TO = "Values"

# http://stackoverflow.com/questions/3424899/whats-the-simplest-way-to-subtract-a-month-from-a-date-in-python
def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d,month=m, year=y)

def tariff_info():
	print("Available tariffs:")
	df = pd.read_csv("tariffs_csv.csv")
	tariff_list = list(df)
	for i in range(1, len(tariff_list)):
		print(tariff_list[i])
	name = input("Tariff name:\n")
	return comm_tariff(name)

def get_api_info(address, system_capacity, azimuth, tilt, array_type, module_type, losses):
	base_url = "https://developer.nrel.gov/api/pvwatts/v5.json?api_key=t8dXZSeNlDxNDFAtUr6EPG32u3Vs5qjCppqtNyXr&timeframe=hourly"
	addr_add_on = "&address=" + address
	system_capacity_add_on = "&system_capacity=" + system_capacity
	azimuth_add_on = "&azimuth=" + azimuth
	tilt_add_on = "&tilt=" + tilt
	array_type_add_on = "&array_type=" + array_type
	module_type_add_on = "&module_type=" + module_type
	losses_add_on = "&losses=" + losses
	combined_url = requests.get(base_url + addr_add_on + system_capacity_add_on + 
		azimuth_add_on + tilt_add_on + array_type_add_on + module_type_add_on + losses_add_on)
	to_return = combined_url.text
	return to_return

def get_hourly_ac(json_string):
	dict_from_json = json.loads(json_string)
	hourly_ac = dict_from_json['outputs']['ac']
	return hourly_ac

def solar_calcs(hourly_ac_list, tariff):
	last_day = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
	hour = 0
	month = 1
	day = 1
	index = 0
	total_ac_output = 0
	annual_kwh_solar_revenue = 0
	season = "winter"
	cal = USFederalHolidayCalendar()
	holidays = cal.holidays(start=str(YEAR) + '-01-01', end=str(YEAR) + '-12-31').to_pydatetime()
	for i in range(len(hourly_ac_list)):
		total_ac_output += hourly_ac_list[i]
		date = datetime.datetime(YEAR, month, day, 0, 0)
		if date == tariff.seasons['Summer Start']:
			season = "summer"
		if date == tariff.seasons['Winter Start']:
			season = "winter"
		if date.weekday() == 5 or date.weekday() == 6 or date in holidays:
			if season == "winter":
				rate = tariff.rates['kWh Off Peak (winter)']
			if season == "summer":
				rate = tariff.rates['kWh Off Peak (summer)']
		else:
			if season == "winter":
				if hour < int(tariff.hours['Off Peak Morning Start (winter)']) or hour >= int(tariff.hours['Off Peak Evening End (winter)']):
					rate = tariff.rates['kWh Off Peak (winter)']
				elif hour >= int(tariff.hours['Peak Start (winter)']) and hour < int(tariff.hours['Peak End (winter)']):
					rate = tariff.rates['kWh Peak (winter)']
				else:
					rate = tariff.rates['kWh Part Peak (winter)']
			else:
				if hour < int(tariff.hours['Off Peak Morning Start (summer)']) or hour >= int(tariff.hours['Off Peak Evening End (summer)']):
					rate = tariff.rates['kWh Off Peak (summer)']
				elif hour >= int(tariff.hours['Peak Start (summer)']) and hour < int(tariff.hours['Peak End (summer)']):
					rate = tariff.rates['kWh Peak (summer)']
				else:
					rate = tariff.rates['kWh Part Peak (summer)']
		annual_kwh_solar_revenue += float(rate) * hourly_ac_list[i]
		hour += 1
		if hour == 24:
			day += 1
			if day == last_day[month] + 1:
				month += 1
				day = 1
			hour = 0
	return total_ac_output/1000, annual_kwh_solar_revenue/1000

def parse_cust_use():
	input_source = CUST_USE
	info = pd.read_csv("intake example.csv", skiprows = 1)
	date, max_peak_demand, part_peak_demand, max_demand, peak_consump, part_peak_consump, off_peak_consump = ([] for i in range(7))
	for index, row in info.iterrows(): 
		if index >= 12:
			continue;
		else:
			date.append(row['Billing Period End Date'])
			max_peak_demand.append(row['Max Peak'])
			part_peak_demand.append(row['Part Peak'])
			max_demand.append(row['Max Demand'])
			peak_consump.append(row['Peak'])
			part_peak_consump.append(row['Part Peak.1'])
			off_peak_consump.append(row['Off Peak'])
	date = [datetime.datetime.strptime(x, "%m/%d/%y") for x in date]
	date = [datetime.datetime(x.year, x.month, x.day, 0, 0) for x in date]
	max_peak_demand = fix_nan(max_peak_demand)
	part_peak_demand = fix_nan(part_peak_demand)
	max_demand = fix_nan(max_demand)
	peak_consump = fix_nan(peak_consump)
	part_peak_consump = fix_nan(part_peak_consump)
	off_peak_consump = fix_nan(off_peak_consump)
	lists = [date, max_peak_demand, part_peak_demand, max_demand, peak_consump, part_peak_consump, off_peak_consump]
	return lists

def fix_nan(list):
	to_return = [0 if math.isnan(x) else x for x in list]
	return to_return

def customer_dates(lists, tariff):
	beginning_date, ending_date, season, max_peak_demand, part_peak_demand, max_demand, peak_consump, part_peak_consump, off_peak_consump  = ([] for i in range(9))
	beginning_date = [monthdelta(lists[0][i], -1) for i in range(12)]
	max_peak_demand = lists[1]
	part_peak_demand = lists[2]
	max_demand = lists[3]
	peak_consump = lists[4]
	part_peak_consump = lists[5]
	off_peak_consump = lists[6]
	coll_lists = [max_peak_demand, part_peak_demand, max_demand, peak_consump, part_peak_consump, off_peak_consump]
	ending_date = lists[0]
	summer_found = False
	winter_found = False
	for j in range(len(beginning_date)):
		median_month = math.floor((beginning_date[j].month + ending_date[j].month)/2)
		if beginning_date[j].month == 12 and ending_date[j].month == 1:
			median_month = 0
		if tariff.seasons["Summer Start"].month < median_month < tariff.seasons["Winter Start"].month:
			season.append("summer")
		else:
			season.append("winter")
	for i in range(len(beginning_date)):
		beginning_to_compare = beginning_date[i].replace(year = 2000)
		ending_to_compare = ending_date[i].replace(year = 2000)
		winter_to_compare = tariff.seasons["Winter Start"].replace(year = 2000)
		summer_to_compare = tariff.seasons["Summer Start"].replace(year = 2000)
		if beginning_to_compare < winter_to_compare < ending_to_compare and winter_found == False:
			beginning_date.insert(i + 1, tariff.seasons["Winter Start"].replace(year = beginning_date[i].year))
			ending_date.insert(i, tariff.seasons["Winter Start"].replace(year = beginning_date[i].year))
			season.insert(i + 1, "winter")
			for listx in coll_lists:
				listx.insert(i + 1, 0)
			winter_found = True
		if beginning_to_compare < summer_to_compare < ending_to_compare and summer_found == False:
			beginning_date.insert(i + 1, tariff.seasons["Summer Start"].replace(year = beginning_date[i].year))
			ending_date.insert(i, tariff.seasons["Summer Start"].replace(year = beginning_date[i].year))
			season.insert(i + 1, "summer")
			for listx in coll_lists:
				listx.insert(i + 1, 0)
			summer_found = True
	to_return = [beginning_date, ending_date, season]
	for listx in coll_lists:
		to_return.append(listx)
	return to_return

def customer_calcs(lists, tariff):
	max_all_demand, total_consump, max_peak_demand_dol, part_peak_demand_dol, max_demand_dol, total_demand_dol, peak_consump_dol, part_peak_consump_dol, off_peak_consump_dol, total_consump_total, grand_total = ([] for i in range(11))
	for i in range(len(lists[3])):
		max_all_demand.append(max(lists[3][i], lists[4][i], lists[5][i]))

	for j in range(len(lists[6])):
		total_consump.append(lists[6][j] + lists[7][j] + lists[8][j])

	max_peak_demand_dol = [tariff.rates["Max kW Peak (summer)"] * x for x in lists[3]]

	for k in range(len(lists[4])):
		if lists[2][k] == "summer":
			part_peak_demand_dol.append(tariff.rates['Part kW Peak (summer)'] * lists[4][k])
			max_demand_dol.append(tariff.rates['Anytime kW Peak (summer)'] * lists[5][k])
			peak_consump_dol.append(tariff.rates['kWh Peak (summer)'] * lists[6][k])
			part_peak_consump_dol.append(tariff.rates['kWh Part Peak (summer)'] * lists[7][k])
			off_peak_consump_dol.append(tariff.rates['kWh Off Peak (summer)'] * lists[8][k])
		else:
			part_peak_demand_dol.append(tariff.rates['Part kW Peak (winter)'] * lists[4][k])
			max_demand_dol.append(tariff.rates['Anytime kW Peak (winter)'] * lists[5][k])
			peak_consump_dol.append(tariff.rates['kWh Peak (winter)'] * lists[6][k])
			part_peak_consump_dol.append(tariff.rates['kWh Part Peak (winter)'] * lists[7][k])
			off_peak_consump_dol.append(tariff.rates['kWh Off Peak (winter)'] * lists[8][k])
		total_demand_dol.append(max_peak_demand_dol[k] + part_peak_demand_dol[k] + max_demand_dol[k])
		total_consump_total.append(peak_consump_dol[k] + part_peak_consump_dol[k] + off_peak_consump_dol[k])
		grand_total.append(total_demand_dol[k] + total_consump_total[k])

	complete_array = [lists[0], lists[1], lists[2], lists[3], lists[4], lists[5], max_all_demand, lists[6], 
		lists[7], lists[8], total_consump, max_peak_demand_dol, part_peak_demand_dol, max_demand_dol, 
		total_demand_dol, peak_consump_dol, part_peak_consump_dol, off_peak_consump_dol, total_consump_total, grand_total]
	return complete_array

def sanitize_cust_calcs(finish):
	finish[0] = [datetime.date(x.year, x.month, x.day) for x in finish[0]]
	finish[1] = [datetime.date(x.year, x.month, x.day) for x in finish[1]]
	data_df = pd.DataFrame({"Beginning Date": finish[0], "Ending Date": finish[1], "Season": finish[2], 
		"Max Peak Demand": finish[3], "Part Peak Demand": finish[4], "Max Demand": finish[5], 
		"Max Off All Demand": finish[6], "Peak Consumption": finish[7], "Part Peak Consumption": finish[8], 
		"Off Peak Consumption": finish[9], "Total Consumption": finish[10], "Max Peak Demand Dollars": finish[11],
		"Part Peak Demand Dollars": finish[12], "Max Demand Dollars": finish[13], "Total Demand Dollars": finish[14],
		"Peak Consumption Dollars": finish[15], "Part Peak Consumption Dollars": finish[16], 
		"Off Peak Consumption Dollars": finish[17], "Total Consumption Dollars": finish[18], 
		"Grand Total": finish[19]})
	ordered_data = data_df[["Beginning Date", "Ending Date", "Season", "Max Peak Demand", "Part Peak Demand",
		"Max Demand", "Max Off All Demand", "Peak Consumption", "Part Peak Consumption", "Off Peak Consumption",
		"Total Consumption", "Max Peak Demand Dollars", "Part Peak Demand Dollars", "Max Demand Dollars",
		"Total Demand Dollars", "Peak Consumption Dollars", "Part Peak Consumption Dollars", 
		"Off Peak Consumption Dollars", "Total Consumption Dollars", "Grand Total"]]
	return ordered_data

def sanitize_tariff_rates(tariff):
	rates_df = pd.DataFrame(list(tariff.rates.items()), columns = ["Rate", "Price"])
	rates_df = rates_df.sort_values(by = "Rate")
	return rates_df

def sanitize_values(system_capacity, calc, finish, tariff):
	system_capacity = float(system_capacity)
	descrip_list = ["Tariff", "PV System Size", "Specific Annual Production", "kWh PV Generation", "Annual Solar Revenue",
		"Solar $/kWh Revenue", "Consumption (kWh) Offset", "Consumption ($$$) Offset", "Demand (kW) Offset",
		"Demand ($$$) Offset", "Total Bill (Cons + Dem) Offset"]
	units = [0, "kW-DC", "kWh / kW-AC / yr", "kWh / yr", "/ yr", "/ kWh", 0, 0, 0, 0, 0]
	values = [tariff.name, system_capacity, calc[0]/system_capacity, calc[0], calc[1], calc[1]/calc[0],
		calc[0]/sum(finish[10]), calc[1]/sum(finish[18]), 0, 0, min(calc[1], sum(finish[18]))/sum(finish[19])]
	info_df = pd.DataFrame({"Description": descrip_list, "Values": values, "Units": units})
	ordered_info = info_df[["Description", "Values", "Units"]]
	return ordered_info

def main():
	addr = input("Address:\n")
	system_capacity = input("System capacity:\n")
	azimuth = input("Azimuth:\n")
	tilt = input("Tilt:\n")
	array_type = input("Array type:\n")
	module_type = input("Module type:\n")
	losses = input("Losses:\n")
	url_string = get_api_info(addr, system_capacity, azimuth, tilt, array_type, module_type, losses)
	ac_hourly = get_hourly_ac(url_string)
	tariff = tariff_info()
	calc = solar_calcs(ac_hourly, tariff)
	lists = parse_cust_use()
	parsed = customer_dates(lists, tariff)
	finish = customer_calcs(parsed, tariff)

	rates_df = sanitize_tariff_rates(tariff)
	ordered_cust_data = sanitize_cust_calcs(finish)
	ordered_info = sanitize_values(system_capacity, calc, finish, tariff)

	book = load_workbook(OUTPUT)
	writer = pd.ExcelWriter(OUTPUT, engine = 'openpyxl')
	writer.book = book
	writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
	ordered_cust_data.to_excel(writer, sheet_name = SHEET_TO_PRINT_TO, index = False)
	rates_df.to_excel(writer, sheet_name = SHEET_TO_PRINT_TO, index = False, startrow = 15)
	ordered_info.to_excel(writer, sheet_name = SHEET_TO_PRINT_TO, index = False, startrow = 28)
	writer.save()

main()
