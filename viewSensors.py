# steve.a.mccluskey@gmail.com
# Utility to display all available OneWire temp sensors on the bus.
'''
Updates:


7/25/24: added threading to grab sensors values concurrently and changed the file used to grab temps to "/temperature" instead of "w1_slave". I dont know if I'm going to keep it that way yet, since there is no CRC in that file.


'''


import os
import time
import glob
import json
import datetime
import os.path
from os import path
import threading


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

degree_sign = u"\N{DEGREE SIGN}"


def read_temp_f(file):
	device_file = "/sys/bus/w1/devices/" + file + "/temperature"
	if (path.exists(device_file)):
		try:
			f = open (device_file, 'r')
			temp_string = f.read()
			f.close()

			temp_c = float(temp_string) / 1000.0
			temp_f = temp_c * 1.8 + 32.0
			return format(temp_f, '.1f')
		except:
			return "OFF"
	else:
		return "OFFLINE"

def read_temp(file):
	device_file = "/sys/bus/w1/devices/" + file + "/w1_slave"
	if (path.exists(device_file)):
		try:
			f = open (device_file, 'r')
			lines = f.readlines()
			f.close()

			pos = lines[1].find('t=')

			if (pos != -1):
				temp_string= lines[1][pos + 2:]
				temp_c = float(temp_string) / 1000.0
				temp_f = temp_c * 1.8 + 32.0
				return format(temp_c, '.1f'), format(temp_f, '.1f')
		except:
			return "OFF", "OFF"
	else:
		return "OFF", "OFF"

def multi_threaded_file_reader(file_paths):
	threads = []
	results = {}

	def read_file_thread(file_path):
		result = read_temp_f(file_path)
		results[file_path] = result

	for file_path in file_paths:
		thread = threading.Thread(target = read_file_thread, args = (file_path,))
		threads.append(thread)
		thread.start()

	for thread in threads:
		thread.join()
	
	return results

while True:
	
	sensorIds = os.listdir("/sys/bus/w1/devices")
	results = multi_threaded_file_reader(sensorIds)
#	print(tempF)
	print("Found " + str((len(sensorIds) - 1)) + " devices on bus:")
	i = 1

	for file_path, content in results.items():
		if (file_path.find('28-') != -1):
			print (str(i).zfill(2) + ") Sensor ID: " + str(file_path) + ". Temp = " + str(content) + degree_sign + "F.")
			i += 1

	print(" ")



	time.sleep(2)

