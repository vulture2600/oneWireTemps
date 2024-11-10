'''
steve.a.mccluskey@gmail.com
testing reading Adafruit ADS1115 ADC breakout board and writing to influx


'''



import time
import Adafruit_ADS1x15
import smbus
import os
import time
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

adc = Adafruit_ADS1x15.ADS1115()

channel     = 0
ch0GAIN     = 1
ch0maxPSI   = 100
ch0minPSI   = 0
ch0minADC   = 4100
ch0maxADC   = 32768

while True:
    print("Reading ADC:")
    try:
        series  = []
        value   = adc.read_adc(channel, gain = ch0GAIN)
        psi = format((((value - ch0minADC) * (ch0maxPSI - ch0minPSI)) / (ch0maxADC - ch0minADC) + ch0minPSI), '.1f')
        print (psi, "   ", value)

        point = {
            "measurement": "pressures",
            "tags": {
                "sensor":   1,
                "location": "manifold",
                "id":       "i2c:0x44",
                "channel":  channel,
                "type":     "ADS1115",
                "title":    "Manifold Pressure"
            },

            "fields": {
                "pressure": psi
            }

        }
        series.append(point)

    except:
        print("ADC not responding.")

    try:
        client.write_points(series)
        print("Data posted to DB.")

        result = client.query('select * from "pressures" where time >= now() - 5s and time <= now()')
        print("QUERY RECIEVED")
        print("")
        print(result)
    except:
        print("Server timeout")
        print("")

    time.sleep(2)

