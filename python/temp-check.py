#!/usr/bin/python
# Kevin Hinds http://www.kevinhinds.com
# License: GPL 2.0
import datetime as dt
import time, json, string, cgi, subprocess, json
import settings as settings
import Adafruit_DHT
import pprint
pp = pprint.PrettyPrinter(indent=4)
import requests

# Raspberry Pi with DHT sensor - connected to GPIO16 / Pin 36
sensor = Adafruit_DHT.DHT22
pin = 4

# get current date and time
date=dt.datetime.now()

# get 10 readings and average, in case the humidistat is inaccurate
count, readingCount, avgTemperature, avgHumidity = [ 0, 0, 0, 0 ]
while (count < 10):
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    if humidity is not None and temperature is not None:
        print (humidity)
        print (temperature)
        avgTemperature = avgTemperature + temperature
        avgHumidity = avgHumidity + humidity
        readingCount = readingCount + 1
    count = count + 1
    
# get the average of the readings
insideTemperature = int((avgTemperature / readingCount) * 9/5 + 32)
insideTemperature = insideTemperature + settings.dht22Adjust
insideHumidity = int((avgHumidity / readingCount))

# get current forecast from location
weatherInfo = json.loads(subprocess.check_output(['curl', settings.weatherAPIURL]))
currentConditions = weatherInfo['current']

apparentTemperature = str(int(currentConditions['feels_like']))
humidity = str(int(currentConditions['humidity'] * 100))

# minutely conditions, limit the characters to 30 in the summary
summary = str(currentConditions['weather'][0]['description'])
summary = (summary[:27] + '...') if len(summary) > 29 else summary

# `apparentTemperature` and `insideTemperature` as JSON object for file
weatherData = {
    "apparentTemperature": apparentTemperature,
    "insideTemperature": insideTemperature
}

# Write JSON data to file
with open('weatherInfo.json', 'w') as file:
    json.dump(weatherData, file)

# post to datahub
r = requests.post("https://" + settings.deviceLoggerAPI + "/api/log/", data={'device': 'temp-check-bedroom', 'value1': str(insideTemperature), 'value2': str(insideHumidity) , 'value3': str(apparentTemperature), 'value4': str(humidity), 'value5': str(summary)})
print(r.status_code, r.reason)
print(r.text)
