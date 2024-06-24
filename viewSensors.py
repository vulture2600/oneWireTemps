# steve.a.mccluskey@gmail.com
# Utility to display all available OneWire temp sensors on the bus.



import os
import time
import glob
import json
import datetime
import os.path
from os import path


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

degree_sign = u"\N{DEGREE SIGN}"

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


while True:
	try:
		sensorIds = os.listdir("/sys/bus/w1/devices")
		print("Found " + str((len(sensorIds) - 1)) + " devices on bus:")
		i = 1;
		for sensor in range (len(sensorIds)):
			if (sensorIds[sensor].find('28-') != -1):
				tempC, tempF = read_temp(sensorIds[sensor])
				print (str(i) + ") Sensor ID: " + str(sensorIds[sensor]) + ". Temp = " + str(tempC) + degree_sign + "C, " + str(tempF) + degree_sign + "F.")
				i += 1

		print(" ")

	except:
		pass

	time.sleep(2)

