import requests
import json
from tariff import tariff

def tariff_info():
	name = input("Tariff name:\n")
	return tariff(name)

def get_inputs():
	addr = input("Address:\n")
	system_capacity = input("System capacity:\n")
	azimuth = input("Azimuth:\n")
	tilt = input("Tilt:\n")
	array_type = input("Array type:\n")
	module_type = input("Module type:\n")
	losses = input("Losses:\n")
	return addr, system_capacity, azimuth, tilt, array_type, module_type, losses

def get_api_info(address, system_capacity, azimuth, tilt, array_type, module_type, losses):
	base_url = "https://developer.nrel.gov/api/pvwatts/v5.json?api_key=t8dXZSeNlDxNDFAtUr6EPG32u3Vs5qjCppqtNyXr"
	addr_add_on = "&address=" + address
	system_capacity_add_on = "&system_capacity=" + system_capacity
	azimuth_add_on = "&azimuth=" + azimuth
	tilt_add_on = "&tilt=" + tilt
	array_type_add_on = "&array_type=" + array_type
	module_type_add_on = "&module_type=" + module_type
	losses_add_on = "&losses=" + losses
	combined_url = requests.get(base_url + addr_add_on + system_capacity_add_on + azimuth_add_on + tilt_add_on + array_type_add_on + module_type_add_on + losses_add_on)
	to_return = combined_url.text
	return to_return

def get_monthly_ac(json_string):
	dict_from_json = json.loads(json_string)
	monthly_ac = dict_from_json['outputs']['ac_monthly']
	return monthly_ac

def main():
	addr = "2800 Woodview Court"
	system_capacity = "4"
	azimuth = "180"
	tilt = "40"
	array_type = "1"
	module_type = "1"
	losses = "10"
	# inputs = get_inputs()
	# addr = inputs[0]
	# system_capacity = inputs[1]
	# azimuth = inputs[2]
	# tilt = inputs[3]
	# array_type = inputs[4]
	# module_type = inputs[5]
	# losses = inputs[6]
	url_string = get_api_info(addr, system_capacity, azimuth, tilt, array_type, module_type, losses)
	ac_monthly = get_monthly_ac(url_string)
	tariff = tariff_info()
	print(tariff.name)
	print(tariff.seasons)


main()
