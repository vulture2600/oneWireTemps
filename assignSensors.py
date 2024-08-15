''' steve.a.mccluskey@gmail.com
 Utility that shows all OneWire temp sensors on the bus and allows you to assign them to the rooms and writes the configuration 
 to the sensors_config.py file.

Updates: 
7/6/24 - spent the last few weeks revamping this to a pretty funciontal proof of concept. still planning to implement non number input error handling when selecting from list. otherwise, it appears things seem to be working as they should.

7/18/24 - decided to show current temp when showing current config, which takes longer to collect each sensor, but if its offline it wont show up in either list. that led me to find that get_temp() wasnt able to handle a sensor thats offline like in my other script. 

'''




import logging
import os
import ast
import os.path
from os import path
import threading
import datetime

degree_sign = u"\N{DEGREE SIGN}"

config_file = "sensors_config2.py"
log_file    = "sensor_log.py"

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
sensorIds = os.listdir("/sys/bus/w1/devices")

def key_exists(roomID, keys):
	'''recursively check if key exists in config dict'''
	if keys and roomID:
		return key_exists(roomID.get(keys[0]), keys[1:])

	return not keys and roomID is not None
#end key_exists()

def multi_threaded_file_reader(ROOMS):
	threads = []
	results = {}


	def read_file_thread(file_path):
		result = read_temp(file_path)
		results[file_path] = result

	for i in range (len(ROOMS)):
		room_id = list(ROOMS.keys())[i]
		if key_exists(ROOMS, [room_id, 'id']):
			sensor_id = ROOMS.get(room_id, {}).get('id')
			thread = threading.Thread(target = read_file_thread, args = (sensor_id,))
			threads.append(thread)
			thread.start()

	for thread in threads:
		thread.join()

	return results


#def get_assignments():
	'''get assignments by room, testing multi threading'''
	print("ASSIGNMENTS BY ROOM ID:")
	print("Found " + str(len(ROOMS)) + " room IDs in configuration file.")
	print("")
	results = multi_threaded_file_reader(ROOMS)
#	print(results)
	#length of config file:
	for i in range(len(ROOMS)):
		room_id 		  = list(ROOMS.keys())[i]
		room_id_in_quotes = str("'" + room_id + "'")

		if key_exists(ROOMS, [room_id, 'title']):
			title = str("'" + ROOMS.get(room_id, {}).get('title') + "'")

		else:
			title = "Untitled"

		if key_exists(ROOMS, [room_id, 'id']):
			sensor_id = ROOMS.get(room_id, {}).get('id')
			if (sensor_id != "Unassigned"):
				print(str(i + 1).zfill(2) + ") ID: " + str(room_id_in_quotes.ljust(22, ' ')) + "Title: " + str(title.ljust(30, ' ')) + "Assigned to : " +  str(sensor_id).rjust(5, ' ') + ". Temp = " + str(results.items()) + degree_sign + "F.")
			else:
				print(str(i + 1).zfill(2) + ") ID: " + str(room_id_in_quotes.ljust(22, ' ')) + "Title: " + str(title.ljust(30, ' ')) + "Assigned to : " +  str(sensor_id).rjust(5, ' ') + ".")

		else:
			print(str(i + 1).zfill(2) + ") " + str(room_id_in_quotes.ljust(22, ' ')) + ": unassigned.")

	print(" ")
	return
#end get_assignments()

def get_assignments():
	'''get assignments by room, current'''
	print("ASSIGNMENTS BY ROOM ID:")
	print("Found " + str(len(ROOMS)) + " room IDs in configuration file: '" + str(config_file) + "'.")
	print("")
	#length of config file:
	for i in range(len(ROOMS)):
		room_id 		  = list(ROOMS.keys())[i]
		room_id_in_quotes = str("'" + room_id + "'")

		if key_exists(ROOMS, [room_id, 'title']):
			title = str("'" + ROOMS.get(room_id, {}).get('title') + "'")

		else:
			title = "Untitled"

		if key_exists(ROOMS, [room_id, 'id']):
			sensor_id = ROOMS.get(room_id, {}).get('id')
			if (sensor_id != "Unassigned"):
				print(str(i + 1).zfill(2) + ") ID: " + str(room_id_in_quotes.ljust(23, ' ')) + "Title: " + str(title.ljust(30, ' ')) + "Assigned to: " +  str(sensor_id).rjust(5, ' ') + ". Temp = " + str(read_temp(sensor_id)) + degree_sign + "F.")
			else:
				print(str(i + 1).zfill(2) + ") ID: " + str(room_id_in_quotes.ljust(23, ' ')) + "Title: " + str(title.ljust(30, ' ')) + "Assigned to: " +  str(sensor_id).rjust(5, ' ') + ".")

		else:
			print(str(i + 1).zfill(2) + ") " + str(room_id_in_quotes.ljust(23, ' ')) + ": unassigned.")

	print(" ")
	return
#end get_assignments()


def read_temp(file):
	'''read file generated by 1wire module in linux kernel'''
	device_file = "/sys/bus/w1/devices/" + file + "/w1_slave"
	if (path.exists(device_file)):
		try:
			f 		= open (device_file, 'r')
			lines 	= f.readlines()
			f.close()

			equals_pos = lines[1].find('t=')

			if (equals_pos != -1):
				temp_string = lines[1][equals_pos + 2:]
				temp_c 		= float(temp_string) / 1000.0
				temp_f 		= format(float(temp_c * 9.0 / 5.0 + 32.0), '.1f')
				return temp_f
		except:
			return "***OFFLINE***"
	else:
		return "***OFFLINE***"
#end read_temp()


def reassign_sensors_to_rooms():
	'''reassigns all sensors to rooms'''
	print("")
	print("REASSIGN ALL SENSORS:")
	sensorIds = os.listdir("/sys/bus/w1/devices")
	roomIDs             = [0] * len(ROOMS)
	assigned            = [0] * len(ROOMS)
	title               = [0] * len(ROOMS)
	sensorNewAssignment = ["Unassigned"] * len(ROOMS)

	for i in range(len(ROOMS)):
		roomIDs[i] = list(ROOMS.keys())[i]
		if key_exists(ROOMS, [roomIDs[i], 'title']):
			title[i] = ROOMS.get(roomIDs[i], {}).get('title')

		assigned[i] = False
	print("")

	for sensor in range (len(sensorIds)):
		if (sensorIds[sensor].find('28-') != -1):
		#skip w1_bus_master1 folder

			print("Assign " + str(sensorIds[sensor]) + " to:")
			for i in range(len(ROOMS)):
				if (assigned[i] == False):
					print(str(i + 1).zfill(2) + "): '" + str(title[i]) + "'")

			print(" ")
			print("Input 1 - " + str(len(ROOMS)) + ". Enter zero to leave unassigned.")
			assignment = int(input())

			while (assignment > len(ROOMS)) or (assigned[assignment - 1] != False and assignment != 0):
				if (assignment > len(ROOMS)):
					print("Assignment out of range. Please enter 0 - " + str(len(ROOMS)) + ".")
					assignment = int(input())

				elif (assigned[assignment - 1] != False and assignment != 0):
					print("Sensor already assigned. Please choose from list.")
					assignment = int(input())

			if (assignment == 0):
				print("Sensor " + str(sensorIds[sensor]) + " remains unassigned.")
				print("")

			for x in range(1, len(sensorIds)):
				if (assignment == x) :
					print("Sensor " + str(sensorIds[sensor]) +  " assigned to '" + str(roomIDs[x - 1]) + "'")
					sensorNewAssignment[x - 1] 	= str(sensorIds[sensor])
					assigned[x - 1] 			= True
					print("")
	
	with open(log_file, "a") as log:
		log.write("All sensors resassigned. " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		log.write("\n")
	write_config(roomIDs, sensorNewAssignment, title, None)
	print("")
	return
#end reassign_sensors_to_rooms()


def write_config(roomID, sensorID, title, newRoom):
	'''writes config file'''
	with open ("sensors_config2.py", 'w') as f:
		f.write("{")
		f.write("\n")

		for i in range (len(roomID)):
			f.write("\t\"")
			f.write(roomID[i])
			f.write("\": {\n\t\t")
			f.write("\"id\": \"")
			f.write(sensorID[i])
			f.write("\",\n\t\t")
			f.write("\"title\": \"")
			f.write(title[i])
			f.write("\"\n\t}")

			if (i < len(ROOMS) - 1):
				f.write(",")
				f.write("\n")

		if newRoom is not None:
			f.write(",\n")
			f.write("\t\"")
			f.write(newRoom[0])
			f.write("\": {\n\t\t")
			f.write("\"id\": \"")
			f.write(newRoom[1])
			f.write("\", \n\t\t")
			f.write("\"title\": \"")
			f.write(newRoom[2])
			f.write("\"\n\t}")

		f.write("\n}")
		f.close()

	print("CONFIG FILE WRITTEN!")
	print("")
	return
#end write_config()


def assign_unassigned_sensors_to_rooms():
	'''shows only unassigned sensors and unassigned rooms'''
	print("")
	print("REASSIGN ONLY UNASSIGNED SENSORS:")
	print("")

	sensorNewAssignment = []
	sensorNewRoom       = []
	unassignedSensors   = []
	unassignedRooms     = []

	print("SENSORS FOUND ON BUS THAT ARE NOT ASSIGNED TO ROOMS:")
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
				unassignedSensors.append(sensorIds[sensor])
				print("Sensor ID: " + str(sensorIds[sensor]) + " UNASSIGNED. Temp = " + (str(read_temp(sensorIds[sensor])) + degree_sign + "F."))
#	got all unassigned sensors.

	print(" ")
	print("ROOM IDs THAT HAVE NO ASSIGNED SENSOR:")
	for i in range(len(ROOMS)):
		room_id = list(ROOMS.keys())[i]

		if key_exists(ROOMS, [room_id, 'id']):
			sensor_id = ROOMS.get(room_id, {}).get('id')

			if (sensor_id.find('28-') == -1):
				unassignedRooms.append(room_id)
				room_id_in_quotes = str("'" + room_id + "'")
				print("Room ID: " + str(room_id_in_quotes.ljust(20, ' ')) + " has no assigned sensor.")
#	got all unassigned rooms.

	print(" ")
	print("Found " + str(len(unassignedSensors)) + " unassigned sensors on bus.")
	print("Found " + str(len(unassignedRooms)) +   " rooms with no assigned sensors.")
	print(" ")

	if (len(unassignedSensors) == 0):
		print("NO UNASSIGNED SENSORS FOUND.")
		print("")
		return

	print("Assign to unassigned rooms? Press 1 to assign them or 2 to return.")
	textInput = int(input())

	if (textInput == 1):
		if len(unassignedRooms) > len(unassignedSensors):
			assigned = [False] * len(unassignedRooms)

		else:
			assigned = [False] * len(unassignedSensors)

		for i in range(len(unassignedSensors)):
			print("Assign " + str(unassignedSensors[i]) + " to: ")

			for j in range(len(unassignedRooms)):
				if (assigned[j] == False):
					print(str(j + 1).zfill(2) + "): '" + str(unassignedRooms[j]) + "'")

			print(" ")
			print("Input 1 - " + str(len(unassignedRooms)) + ". Enter zero to leave unassigned.")
			assignRoom = int(input())


			while (assignRoom > len(unassignedRooms)) or (assigned[assignRoom - 1] != False and assignRoom != 0):
				if (assignRoom > len(unassignedRooms)):
					print("Assignment out of range. Please enter 0 - " + str(len(unassignedRooms)) + ".")
					assignRoom = int(input())

				elif (assigned[assignRoom - 1] != False and assignRoom != 0):
					print("Sensor already assigned. Please choose from list.")
					assignRoom = int(input())

			if (assignRoom == 0):
				print("Sensor " + str(unassignedSensors[i]) + " remains unassigned.")
				print("")

			for x in range(1, len(unassignedSensors) + 1):
				if (assignRoom == x):
					print("Sensor " + str(unassignedSensors[i]) + " assigned to '" + str(unassignedRooms[x - 1]) + "'")
					sensorNewAssignment.append(str(unassignedSensors[i]))
					sensorNewRoom.append(str(unassignedRooms[i]))
					assigned[x - 1] = True
					print("")
					break


	#	build new config:
		title               = [0] * len(ROOMS)
		roomID              = [0] * len(ROOMS)
		sensorID            = [0] * len(ROOMS)

		for i in range(len(ROOMS)):
			roomID[i] = list(ROOMS.keys())[i]

			if key_exists (ROOMS, [roomID[i], 'title']):
				title[i] = str(ROOMS.get(roomID[i], {}).get('title'))

			if key_exists (ROOMS, [roomID[i], 'id']):
				sensorID[i] = (str(ROOMS.get(roomID[i], {}).get('id')))

				if (sensorID[i] == 'Unassigned' or sensorID[i].find('28-') == -1):
					for j in range(len(sensorNewRoom)):
						if (roomID[i] == sensorNewRoom[j]):
							sensorID[i] = sensorNewAssignment[j]

							with open(log_file, "a") as log:
								log.write("Sensor ID '" + sensorID[i] + "' assigned to " + str(roomID[i]) + "'. " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
								log.write("\n")

		print("")
		print("Confirmed. Writing config and log.")
		write_config(roomID, sensorID, title, None)
	return
#end assign_unassigned_sensors_to_rooms()


def remove_sensor_from_room():
	''' allows you to remove a sensor assignment from a room'''
	print("")
	print("REMOVE SENSOR FROM ROOM:")
	print("")
	get_assignments()
	print("")
	print("Which room ID would you like to remove sensor from? Enter 0 to cancel.")
	remove = int(input())

	if (remove == 0):
		return

	while (remove > len(ROOMS) or remove == 0):
		print("Selection out for range, please reselect from list. Enter 0 to cancel.")
		remove = int(input())

		if (remove == 0):
			return

	room_id   = [0] * len(ROOMS)
	sensor_id = [0] * len(ROOMS)
	title     = [0] * len(ROOMS)

	for i in range(len(ROOMS)):
		room_id[i] = list(ROOMS.keys())[i]

		if key_exists(ROOMS, [room_id[i], 'title']):
			title[i] = ROOMS.get(room_id[i], {}).get('title')

		if key_exists(ROOMS, [room_id[i], 'id']):
			sensor_id[i] = ROOMS.get(room_id[i], {}).get('id')

	room_id_in_quotes = str("'" + room_id[remove - 1] + "'")
	print("Remove sensor " + str(sensor_id[remove - 1]) + " from room " + str(room_id_in_quotes) + "?")
	print("Press 1 to confirm. Press 2 to exit.")
	confirm = int(input())

	if (confirm == 1):
		print("")
		print("Confirmed. Writing config and log.")

		with open(log_file, "a") as log:
			log.write("Sensor ID '" + sensor_id[remove - 1] + "' removed from room ID " + str(room_id_in_quotes) + "'. " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
			log.write("\n")

		sensor_id[remove - 1] = "Unassigned"
		write_config(room_id, sensor_id, title, None)

	return
#end remove_sensor_from_room()


def add_a_room():
	'''add new room'''
	print("ADD NEW ROOM:")
	print("New room ID? 20 characters max. No spaces or special characters.")
	newRoomID = input()

	while (len(newRoomID) > 20):
		print("Length must be less than 20 characters. Please re-enter:")
		newRoomID = input()

	print("New room ID: '" + str(newRoomID) + "'.")
	print("Room title?")
	newRoomTitle = input()

	while (len(newRoomTitle) > 30):
		print("Length must be less than 30 characters. Please re-enter:")
		newRoomTitle = input()

	print("New room title: '" + str(newRoomTitle) + "'.")
	print(" ")
	print("Does this look correct? Press 1 to confirm or 2 to retry:")
	print("New room ID: '" + str(newRoomID) + "'. New room title: '" + str(newRoomTitle) + "'.")
	confirm = int(input())

	if (confirm == 1):
		print("New room added!")

	else:
		add_a_room()

	print(" ")
	print("Press 1 to add new room to config file or press 2 to exit.")
	assign = int(input())

	if (assign == 1):
		newData 	= [newRoomID, "Unassigned", newRoomTitle]
		room_id   	= [0] * len(ROOMS)
		sensor_id 	= [0] * len(ROOMS)
		title     	= [0] * len(ROOMS)

		for i in range(len(ROOMS)):
			room_id[i]   = list(ROOMS.keys())[i]
			sensor_id[i] = ROOMS.get(room_id[i], {}).get('id')
			title[i]     = ROOMS.get(room_id[i], {}).get('title')

		with open(log_file, "a") as log:
			log.write("New Room ID '" + str(newRoomID) + "' added with title: '" + str(newRoomTitle) + "'. " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
			log.write("\n")

		write_config(room_id, sensor_id, title, newData)

	return
#end add_a_room()


def edit_room():
	print("EDIT A ROOM:")
	print("Do you want to:")
	print("1) Change room ID?")
	print("2) Change room title?")
	edit = int(input())

	if (edit == 1):
		print("CHANGE ROOM ID:")
		print("Which room ID would you like to change? Enter 0 to cancel.")
		room_id   = [0] * len(ROOMS)
		sensor_id = [0] * len(ROOMS)
		title     = [0] * len(ROOMS)

		for i in range(len(ROOMS)):
			room_id[i]   = list(ROOMS.keys())[i]
			sensor_id[i] = ROOMS.get(room_id[i], {}).get('id')
			title[i]     = ROOMS.get(room_id[i], {}).get('title')
			print(str(i + 1).zfill(2) + ") " + str(room_id[i]))	

		print("")
		editRoom = int(input())	

		if (editRoom == 0):
			return

		while (editRoom > len(ROOMS) and editRoom != 0):
			print("Selection out of range. Please choose from list. Enter 0 to cancel.")
			editRoom = int(input())

			if (editRoom == 0):
				return

		print("")
		print("CHANGE ID '" + str(room_id[editRoom - 1]) + "' TO:")
		print("Enter new room ID. 20 characters max. No spaces or special characters.")
		newRoomID = input()

		while (len(newRoomID) > 20):
			print("Length must be less than 20 characters. Please re-enter:")
			newRoomID = input()

		print("Changing ID '" + str(room_id[editRoom - 1]) + "' to ID '" + str(newRoomID) + "'.")
		print("The title: '" + str(title[editRoom - 1]) + "' is unchanged.")
		print("")
		print("Press 1 to confirm and write to config file. Press 2 to cancel.")
		edit = int(input())

		if (edit == 1):
			print("Confirmed. Writing config and log:")
			print("")

			with open(log_file, "a") as log:
				log.write("Room ID '" + str(room_id[editRoom - 1]) + "' changed to ID '" + str(newRoomID) + "'. The title: '" + str(title[editRoom - 1]) + "' is unchanged. " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
				log.write("\n")

			room_id[editRoom - 1] = newRoomID
			write_config(room_id, sensor_id, title, None)
			return

	elif (edit == 2):
		print("CHANGE ROOM TITLE:")
		print("Which room title would you like to change? Enter 0 to cancel.")
		room_id   = [0] * len(ROOMS)
		sensor_id = [0] * len(ROOMS)
		title     = [0] * len(ROOMS)

		for i in range(len(ROOMS)):
			room_id[i]   = list(ROOMS.keys())[i]
			sensor_id[i] = ROOMS.get(room_id[i], {}).get('id')
			title[i]     = ROOMS.get(room_id[i], {}).get('title')
			print(str(i + 1).zfill(2) + ") " + str(title[i]))

		print("")
		editTitle = int(input())

		if (editTitle == 0):
			return

		while (editTitle > len(ROOMS) and editTitle != 0):
			print("Selection out of range. Please choose from list. Enter 0 to cancel.")
			editTitle = int(input())

			if (editTitle == 0):
				return

		print("")
		print("CHANGE TITLE '" + str(title[editTitle - 1]) + "' TO:")
		print("Enter new room title:")
		newTitle = input()
		print("Changing title '" + str(title[editTitle - 1]) + "' to title '" + str(newTitle) + "'")
		print("The ID: '" + str(room_id[editTitle - 1]) + "' is unchanged.")
		print("")
		print("Press 1 to confirm and write to config file. Press 2 to cancel.")
		edit = int(input())

		if (edit == 1):
			print("Confirmed. Writing config and log:")
			print("")

			with open(log_file, "a") as log:
				log.write("Title '" + str(title[editTitle - 1]) + "' changed to title '" + str(newTitle) + "'. The ID: '" + str(room_id[editTitle - 1]) + "' is unchanged. " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
				log.write("\n")

			title[editTitle - 1] = newTitle
			write_config(room_id, sensor_id, title, None)
			return

	return
#end edit_room()


def remove_a_room():
	print("REMOVE ROOM FROM CONFIG FILE:")
	get_assignments()
	room_id   = [0] * len(ROOMS)
	sensor_id = [0] * len(ROOMS)
	title     = [0] * len(ROOMS)

	for i in range(len(ROOMS)):
		room_id[i]   = list(ROOMS.keys())[i]
		sensor_id[i] = ROOMS.get(room_id[i], {}).get('id')
		title[i]     = ROOMS.get(room_id[i], {}).get('title')	

	print("Which room would you like to remove from config file? Enter 0 to cancel.")
	removeRoom = int(input())

	if (removeRoom == 0):
		return

	while (removeRoom > len(ROOMS) and removeRoom != 0):
		print("Selection out of range. Please choose from list. Enter 0 to cancel.")
		removeRoom = int(input())

		if (removeRoom == 0):
			return

	print("")
	print("Remove room ID: '" + str(room_id[removeRoom - 1]) + "' with title: '" + str(title[removeRoom - 1]) + "' from config file? Sensor ID: " + str(sensor_id[removeRoom - 1]) + " will be unassigned.")
	print("Press 1 to confirm or 2 to cancel.")
	confirm = int(input())

	if (confirm == 1):
		print("")
		print("Confirmed. Writing config and log.")
		
		with open(log_file, "a") as log:
			log.write("Room ID '" + str(room_id[removeRoom - 1]) + "' with title '" + str(title[removeRoom - 1]) + "' removed from config file. Sensor ID: '" + str(sensor_id[removeRoom - 1]) + "' is now unassigned." + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
			log.write("\n")

		room_id.remove(room_id[removeRoom - 1])
		title.remove(title[removeRoom - 1])
		sensor_id.remove(sensor_id[removeRoom - 1])

		write_config(room_id, sensor_id, title, None)
		print("")
		return

	else:
		return
#end remove_a_room()


def get_devices_on_bus():
	'''shows all devices on 1wire bus and shows room assignments, if any'''
	sensorIds = os.listdir("/sys/bus/w1/devices")
	print("FOUND " + str((len(sensorIds) - 1)) + " DEVICES ON BUS:")

	for sensor in range(len(sensorIds)):
		sensorAssigned = False

		if (sensorIds[sensor].find('28-') != -1):
			for i in range(len(ROOMS)):
				room_id = list(ROOMS.keys())[i]

				if key_exists(ROOMS, [room_id, 'id']):
					sensor_id = ROOMS.get(room_id, {}).get('id')

					if sensor_id == sensorIds[sensor]:
						sensorAssigned = True
						break

			try:
				if (sensorAssigned == True):
					room_id_in_quotes = str("'" + room_id + "'")
					print("Sensor ID: " + str(sensorIds[sensor]) + "  Assigned to: " + str(room_id_in_quotes.ljust(25, ' ')) + "Temp = " + str(read_temp(sensorIds[sensor])) + degree_sign + "F.")

				else:
					print("Sensor ID: " + str(sensorIds[sensor]) + "  Assigned to: ------ UNASSIGNED ------ Temp = " + str(read_temp(sensorIds[sensor])) + degree_sign + "F.")

			except:
				print("Sensor ID: " + str(sensorIds[sensor]) + " ****** OFFLINE ******")

	print("")
	print("")

	return
#end get_devices_on_bus()

def write_log():
	with open(log_file, "a") as log:
		log.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

############################################### STARTS HERE #########################################
if __name__ == "__main__":

	print(" ")
	print("***** SENSOR ASSIGNMENT UTILITY *****")

	while True:
		with open (config_file) as f:
			ROOMS = f.read()

		ROOMS = ast.literal_eval(ROOMS)
		sensorIds = os.listdir("/sys/bus/w1/devices")
		print("")
		print("WHAT WOULD YOU LIKE TO DO?")
		print("1) View current config file, listed by room ID and title; and current temperature.")
		print("2) Show all devices on bus, their room assignments, and current temperature.")
		print("3) Edit sensor assignments.")
		print("4) Edit rooms.")
		print("5) Exit.")
		selection = int(input())
		print(" ")

		if (selection == 1):
			get_assignments()

		elif (selection == 2):
			get_devices_on_bus()

		elif (selection == 3):
			print("---REASSIGN SENSORS--")
			print("Do you want to:")
			print("1) Reassign all sensors to rooms?")
			print("2) Assign only unassigned sensors?")
			print("3) Remove a sensor from a room?")
			sensorReassignType = int(input())
			print("")

			if (sensorReassignType == 1):
				reassign_sensors_to_rooms()

			elif (sensorReassignType == 2):
				assign_unassigned_sensors_to_rooms()

			elif(sensorReassignType == 3):
				print()
				remove_sensor_from_room()

		elif (selection == 4):
			print("---EDIT ROOMS---")
			print("Do you want to:")
			print("1) Add a room?")
			print("2) Edit an existing room?")
			print("3) Remove a room?")
			roomEdit = int(input())
			print("")

			if (roomEdit == 1):
				add_a_room()

			elif(roomEdit == 2):
				edit_room()

			elif(roomEdit == 3):
				remove_a_room()

		elif (selection == 5):
			break

print("Exiting. Good Day!")
#end all


