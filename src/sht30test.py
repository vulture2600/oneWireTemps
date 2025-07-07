"""
steve.a.mccluskey@gmail.com
Get sht30 sensor data and write to InfluxDB.
"""

import os
import time
from dotenv import load_dotenv
import smbus
from influxdb import InfluxDBClient

APP_ENV = os.getenv("APP_ENV")

if APP_ENV is None:
    print("APP_ENV not set, using .env file")
    load_dotenv(override=True)
else:
    print(f"Using .env.{APP_ENV} file")
    load_dotenv(override=True, dotenv_path=f".env.{APP_ENV}")

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

        if int(fTemp) < -40:
            pass

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
                "temp_flt": float(fTemp),
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
