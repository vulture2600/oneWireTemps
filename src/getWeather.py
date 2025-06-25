"""
Updating to write to database instead of json file.
"""

import datetime
import os
import time
from dotenv import load_dotenv
from requests import get
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBServerError

load_dotenv(override=True)

INFLUXDB_HOST = os.getenv("INFLUXDB_HOST")
INFLUXDB_PORT = os.getenv("INFLUXDB_PORT")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
TEMP_SENSOR_DATABASE = os.getenv("TEMP_SENSOR_DATABASE")
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")

#Minneapolis, MN, USA.
lattitude = '44.9398'
longitude = '-93.2533'
units     = 'imperial'
url       = 'http://api.openweathermap.org/data/2.5/onecall?lat=' + lattitude + '&lon=' + longitude + '&exclude=minutely,hourly&appid=' + OPENWEATHERMAP_API_KEY + '&units=' + units

client = InfluxDBClient(INFLUXDB_HOST, INFLUXDB_PORT, USERNAME, PASSWORD, TEMP_SENSOR_DATABASE)
client.create_database(TEMP_SENSOR_DATABASE)
client.get_list_database()
client.switch_database(TEMP_SENSOR_DATABASE)

if client:
    print("client ok!")
else:
    print("server failed!")

while True:
    try:
        weatherData = get(url).json()
        series = []
        dateTimeNow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        point = {
            "measurement": "weather",
            "tags": {
                "location": "Minneapolis"
            },

            "fields": {
                "humidity":               int(weatherData['current']['humidity']),
                "feelsLike":              float(weatherData['current']['feels_like']),
                "currentCondition":       weatherData['current']['weather'][0]['main'],
                "tempHigh":               float(weatherData['daily'][0]['temp']['max']),
                "tempLow":                float(weatherData['daily'][0]['temp']['min']),
                "dailyCondition":         weatherData['daily'][0]['weather'][0]['main'],
                "dailyConditionTomorrow": weatherData['daily'][1]['weather'][0]['main'],
                "tempHighTomorrow":       int(weatherData['daily'][1]['temp']['max']),
                "tempLowTomorrow":        float(weatherData['daily'][1]['temp']['min']),
                "windDirection":          int(weatherData['current']['wind_deg']),
                "windSpeed":              float(weatherData['current']['wind_speed']),
                "windGust":               float(weatherData['daily'][0]['wind_gust']),
                "timeStamp": dateTimeNow
            },
            "time": dateTimeNow
        }

        series.append(point)
        print(point)

    except:
        print("weather failed")
        pass

    try:
        client.write_points(series)
        print("Data posted to DB.")
        result = client.query('select * from "weather" where time >= now() - 10m and time <= now()')
        print(result)

    except InfluxDBServerError as e:
        print("server failed, reason: " + str(e))
        pass

    time.sleep(600) # update every ten minutes (60s x 10 minutes)
