'''
updating to write to database instead of json file
7/14/24 - added time stamps to each db write


'''

import json
import time
import datetime
from requests import get
from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBServerError

#openweathermap.org API Key:
apiKey    = 'ce6df52db591b8e6b40f75c864518b61'
#Minneapolis, MN, USA.
lattitude = '44.9398'
longitude = '-93.2533'
units     = 'imperial'
url       = 'http://api.openweathermap.org/data/2.5/onecall?lat=' + lattitude + '&lon=' + longitude + '&exclude=minutely,hourly&appid=' + apiKey + '&units=' + units

client = InfluxDBClient('192.168.1.34', 8086, 'root', 'password', 'tempSensorData')
client.create_database('tempSensorData')
client.get_list_database()
client.switch_database('tempSensorData')

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
