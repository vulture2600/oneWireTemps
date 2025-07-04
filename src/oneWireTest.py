import os
import time
from pi1wire import Pi1Wire, Resolution
from constants import DEVICES_PATH

all_devices = Pi1Wire().find_all_sensors()
#print (str(all_devices))

sensorIds = os.listdir(DEVICES_PATH)
print (str(sensorIds))
#for s in Pi1Wire().find_all_sensors():

while True:

    all_devices = Pi1Wire().find_all_sensors()

    print("Found " + str(len(all_devices)) + " devices on bus:")
    for temps in all_devices:
        tempF = temps.get_temperature() * 1.8 + 32.0
        print (f'{temps.mac_address} = {tempF:.1f}')

    print("")
    time.sleep(2)
#	s.change_resolution(Resolution.X0_5)
#	print (f'{s.mac_address} = {s.get_temperature():.3f}')

#print(Pi1Wire().find('28000006decbf1'))
