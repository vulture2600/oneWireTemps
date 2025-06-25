"""
steve.a.mccluskey@gmail.com
Testing reading Adafruit ADS1115 ADC breakout board and writing to influx.
"""

import os
import time
import Adafruit_ADS1x15
from dotenv import load_dotenv
from influxdb import InfluxDBClient

load_dotenv(override=True)

INFLUXDB_HOST = os.getenv("INFLUXDB_HOST")
INFLUXDB_PORT = os.getenv("INFLUXDB_PORT")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
SENSOR_DATABASE = os.getenv("SENSOR_DATABASE")

client = InfluxDBClient(INFLUXDB_HOST, INFLUXDB_PORT, USERNAME, PASSWORD, SENSOR_DATABASE)
client.create_database(SENSOR_DATABASE)
client.get_list_database()
client.switch_database(SENSOR_DATABASE)
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
