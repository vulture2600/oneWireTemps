'''
steve.a.mccluskey@gmail.com

testing writing sht30 data to influxdb




'''

import smbus
import time
import os
import glob
import json
import datetime
import os.path
from os import path
from influxdb import InfluxDBClient


client = InfluxDBClient('192.168.1.34', 8086, 'root', 'password', 'SandstoneSensorData')
client.create_database('SandstoneSensorData')
client.get_list_database()
client.switch_database('SandstoneSensorData')
print("client ok!")

bus = smbus.SMBus(1)

while True:
    print("Reading Sensor:")
    try:
        series = []
        bus.write_i2c_block_data(0x44, 0x2C, [0x06])
        time.sleep(0.5)
        data1 = bus.read_i2c_block_data(0x44, 0x00, 6)

        cTemp = ((((data1[0] * 256.0) + data1[1]) * 175) / 65535.0) - 45
        fTemp = format(float((cTemp * 1.8) + 32), '.1f')
        print(str(fTemp), "F")

        humidity = format(float(100 * (data1[3] * 256 + data1[4]) / 65535.0), '.1f')
        print(str(humidity), "%")

        point = {
            "measurement": "temps",

            "tags": {
                "sensor":   1,
                "location": "shedSHT30",
                "id":       "i2c:0x44",
                "type":     "sht30",
                "title":    "Shed SHT30"
            },

            "fields": {
                "temp":     fTemp,
                "humidity": humidity
            }
        }

        series.append(point)

    except:
        print("SHT30 not responding.")

    try:
        client.write_points(series)
        print("Data posted to DB.")

        result = client.query('select * from "temps" where time >= now() - 5s and time <= now()')
        print("QUERY RECIEVED")
        print("")
        print(result)
        
    except:
        print("Server timeout")
        print("")

    time.sleep(10)