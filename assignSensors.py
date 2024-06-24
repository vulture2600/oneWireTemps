# steve.a.mccluskey@gmail.com
# Utility that shows all OneWire temp sensors on the bus and allows you to assign them to the rooms and writes the configuration 
# to the sensors_config.py file.

import os
import time
import glob
import json
import datetime

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

sensorIds = os.listdir("/sys/bus/w1/devices")

def key_exists(roomID, keys):
	'''recursively check if key exists in config dict'''

	if keys and roomID:
		return key_exists(roomID.get(keys[0]), keys[1:])
	return not keys and roomID is not None

def get_assignments():
	'''get assignments by room'''

	from sensors_config2 import ROOMS as ROOMS
	print("ASSIGNMENTS BY ROOM ID:")
	print("Found " + str(len(ROOMS)) + " room IDs in configuration file.")
	print("")
	#length of config file:
	for i in range(len(ROOMS)):
		try:
			room_id = list(ROOMS.keys())[i]
			if key_exists(ROOMS, [room_id, 'id']):
				sensor_id = ROOMS.get(room_id, {}).get('id')
				print(str(i + 1) + ") " + str(room_id) + ": assigned to : " +  str(sensor_id))
			else:
				print(str(i + 1) + ") " + str(room_id) + ": unassigned.")

		except:
			i = i + 1
	print(" ")
#end def

def read_temp(file):
	'''read file generated by 1wire module in linux kernel'''

	device_file = "/sys/bus/w1/devices/" + file + "/w1_slave"
	f = open (device_file, 'r')
	lines = f.readlines()
	f.close()

	equals_pos = lines[1].find('t=')

	if (equals_pos != -1):
		temp_string = lines[1][equals_pos + 2:]
		temp_c = float(temp_string) / 1000.0
		temp_f = format(float(temp_c * 9.0 / 5.0 + 32.0), '.1f')
		return temp_f
	#end if
#end def


def reassign_sensors_to_rooms():
	'''reassigns all sensors to rooms'''

	from sensors_config2 import ROOMS as ROOMS
	roomIDs             = [0] * len(ROOMS)
	assigned            = [0] * len(ROOMS)
	title               = [0] * len(ROOMS)
	sensorNewAssignment = [0] * len(ROOMS)
	for i in range(len(ROOMS)):
		roomIDs[i] = list(ROOMS.keys())[i]
		if key_exists(ROOMS, [roomIDs[i], 'title']):
			title[i] = ROOMS.get(roomIDs[i], {}).get('title')
		assigned[i] = False
	print(" ")
#	print(roomIDs)
#	print(assigned)
#	print(title)
#	print(sensorIds)

	print("")
	for sensor in range (len(sensorIds)):
		if (sensorIds[sensor].find('28-') != -1):
		#skip w1_bus_master1 folder

			print("Assign " + str(sensorIds[sensor]) + " to:")
			for i in range(len(ROOMS)):
				if (assigned[i] == False):
					print(str((i + 1)) + "): " + str(title[i]))

			print(" ")

			print("Input 1 - " + str(len(ROOMS)) + ". Enter zero to leave unassigned.")
			assignment = int(input())

			while (assigned[assignment - 1] != False and assignment != 0):
				print("Sensor already assigned. Please choose from list.")
				assignment = int(input())

			while (assignment > len(ROOMS)):
				print("Assignment out of range. Please enter 0 - " + str(len(ROOMS)) + ".")
				assignment = int(input())

			if (assignment == 0):
				print("Sensor " + str(sensorIds[sensor]) + " remains unassigned.")
				print("")

			for x in range(1, len(sensorIds)):
				if (assignment == x) :
					print("Sensor " + str(sensorIds[sensor]) +  " assigned to " + str(roomIDs[x - 1]))
					sensorNewAssignment[x - 1] = str(sensorIds[sensor])
					assigned[x - 1] = True
					print("")

	write_config(sensorNewAssignment, roomIDs)
	print("Config file written!")
#end def

def write_config(sensorNewAssignment, roomIDs):
	'''writes config file'''
	with open ("sensors_config2.py", 'w') as f:
		f.write("ROOMS = {")
		f.write("\n")
		for i in range (len(ROOMS)):
			f.write("\t\"")
			f.write(list(ROOMS.keys())[i])
			f.write("\": {\n\t\t")
			f.write("\"id\": \"")
			f.write(str(sensorNewAssignment[i]))
			f.write("\",\n\t\t")
			f.write("\"title\": \"")
			f.write(ROOMS[roomIDs[i]]['title'])
			f.write("\"\n\t}")
			if (i < len(ROOMS) -1 ):
				f.write(",")
			f.write("\n")
		f.write("}")
	f.close()
#end write_config()


def assign_unassigned_sensors_to_rooms():
	'''shows only unassigned sensors and unassigned rooms'''
	from sensors_config2 import ROOMS as ROOMS
	print("Sensors found on bus that are unassigned to rooms:")
	for sensor in range(len(sensorIds)):
		sensorAssigned = False
		if (sensorIds[sensor].find('28-') != -1):
			for i in range (len(ROOMS)):
				room_id = list(ROOMS.keys())[i]
				if key_exists(ROOMS, [room_id, 'id']):
					sensor_id = ROOMS.get(room_id, {}).get('id')

					if (sensor_id == sensorIds[sensor]):
						sensorAssigned = True
						break

			if (sensorAssigned != True):
				print("Sensor ID: " + str(sensorIds[sensor]) + " UNASSIGNED. Temp = " + (str(read_temp(sensorIds[sensor])) + "F."))


#def add_a_room():


#starts here:
#print(" ")
#get_assignments()

def get_devices_on_bus():
	'''shows all devices on 1wire bus and shows room assignments, if any'''
	print("FOUND " + str((len(sensorIds) -1)) + " DEVICES ON BUS:")
	from sensors_config2 import ROOMS as ROOMS
	for sensor in range(len(sensorIds)):
		sensorAssigned = False
		if (sensorIds[sensor].find('28-') != -1):
			temp = read_temp(sensorIds[sensor])

			for i in range(len(ROOMS)):
				room_id = list(ROOMS.keys())[i]

				if key_exists(ROOMS, [room_id, 'id']):
					sensor_id = ROOMS.get(room_id, {}).get('id')

					if sensor_id == sensorIds[sensor]:
						sensorAssigned = True
						break

			if (sensorAssigned == True):
				print("Sensor ID: " + str(sensorIds[sensor]) + " assigned to: " + str(room_id) + ". Temp = " + str(temp) + "F.")
			else:
				print("Sensor ID: " + str(sensorIds[sensor]) + " UNASSIGNED. Temp = " + str(temp) + "F.")

#starts here:
print(" ")
get_assignments()
get_devices_on_bus()

print(" ")
print(" ")
print("What would you like to do now?")
print("1) Reassign sensors")
print("2) Add a room")
print("3) Exit")
sensorReassign = input()
#print(str(sensorReassign))

if (sensorReassign == '1'):
	print("Do you want to")
	print("1) Reassign all sensors to rooms?")
	print("2) Assign only unassigned sensors?")
	sensorReassignType = int(input())

	if (sensorReassignType == 1):
		reassign_sensors_to_rooms()

	if (sensorReassignType == 2):
		assign_unassigned_sensors_to_rooms()



if (sensorReassign == '2'):
	print("Add new room:")
	#addNewRoom()


else:
	print("Done.")



#end all


