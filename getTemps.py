'''
steve.a.mccluskey@gmail.com

testing writing temp sensor data to influxDB
uses sensors_config.py as config file

'''


from influxdb import InfluxDBClient
from datetime import datetime
import time
import os
import glob
import json
import os.path
from os import path

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

client = InfluxDBClient('192.168.1.34', 8086, 'root', 'password', 'tempSensorData')
client.create_database('tempSensorData')
client.get_list_database()
client.switch_database('tempSensorData')
print("client ok!")


def read_temp(file):
	device_file = "/sys/bus/w1/devices/" + file + "/w1_slave"
	if (path.exists(device_file)):
		try:
			f = open(device_file, 'r')
			lines = f.readlines()
			f.close()

			position = lines[1].find('t=')

			if (position != -1):
				temp_string = lines[1][position + 2:]
				temp_c = float(temp_string) / 1000.0
				temp_f = format((temp_c * 1.8 + 32.0), '.1f')
				return temp_f
		except:
			return "Off"
	else:
		return "Off"


def key_exists(roomID, keys):
	if keys and roomID:
		return key_exists(roomID.get(keys[0]), keys[1:])
	return not keys and roomID is not None


while True:
	print("Reading Sensors:")
	series = []
	from sensors_config import ROOMS as ROOMS

	#get number of rooms from config file and make arrays:
	count = len(ROOMS)

	for i in range(count):
		try:
			room_id = list(ROOMS.keys())[i]
			if key_exists(ROOMS, [room_id, 'id']):
				sensor_id = ROOMS.get(room_id, {}).get('id')
				temp = read_temp(sensor_id)
			else:
				sensor_id = "unassigned"
				temp = "Off"

			if key_exists(ROOMS, [room_id, 'title']):
				title = ROOMS.get(room_id, {}).get('title')
			else:
				title = "Untitled"

			print("Sensor " + str(i + 1) +  ") collected. Room ID: " + str(room_id) + ". Room title: " + str(title) + ". Sensor ID: " + str(sensor_id) + ", temp = " + str(temp)+ "F.")

			point = {
				"measurement": "temps",
				"tags": {
					"sensor": i + 1,
					"location": room_id,
					"id": sensor_id,
					"type": "ds18b20",
					"title": title
				},

				"fields": {
					"temp": temp
				}
			}

			series.append(point)
		except:
			i = i + 1

	print(str(i + 1) + " sensors collected.")

	try:
		client.write_points(series)
		print("Data posted to DB.")



#bind_location = {'location': 'outside'}
#result = client.query(query, bind_params=bind_location)


#result = client.query('''SELECT * FROM "temps" WHERE "location"='incubator' and time >= now() - 10s and time <= now()''')



		result = client.query('select * from "temps" where time >= now() - 5s and time <= now()')
#		print(result)
		print("Query recieved.")
		print(" ")
	except:
		print("Server timeout")
		print(" ")
