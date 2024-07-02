import smbus
import time
import os
import glob
import json
import datetime
import os.path
from os import path


bus = smbus.SMBus(1)

while True:

    data = {
        "sensors": {},
        "timestamp":[
        ]
    }
    bus.write_i2c_block_data(0x44, 0x2C, [0x06])
    time.sleep(0.5)
    data1 = bus.read_i2c_block_data(0x44, 0x00, 6)

    cTemp = ((((data1[0] * 256.0) + data1[1]) * 175) / 65535.0) - 45
    fTemp = format(float((cTemp * 1.8) + 32), '.1f')
    print(str(fTemp), "F")

    humidity = format(float(100 * (data1[3] * 256 + data1[4]) / 65535.0), '.1f')
    print(str(humidity), "%")

    data["sensors"]["sht30"] = {'id': "sht30", 'temp': str(fTemp), 'humidity': str(humidity)}
    #data["sensors"][str(rooms[i])] = {'id': str(ids[i]), 'temp': str(temps[i])}
    print("1")
    #data["sensors"]["1"] = {'id': "sht30", 'humidity': str(humidity)}

    dateTimeObj = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(str(dateTimeObj))
    data["timestamp"].append({'dateTime': str(dateTimeObj)})

    with open('/var/www/html/mount/data/sht30.json', 'w') as g:
        json.dump(data, g, indent = 2)


    time.sleep(5)

