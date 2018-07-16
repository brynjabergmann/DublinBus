import json
import requests
import time 
import pymysql
from pymysql.err import IntegrityError
from time import sleep, strftime, gmtime
import pymysql.cursors
import datetime
import sys

def dbConnect():
    
    """Connects to the database"""
    
    try:
        db = pymysql.connect(
            host='localhost',
            user='superfint',
            password='Team 8 Project',
            db='dublin_bus'
        )
        
    except Exception as e: 
        sys.exit("Cannot connect to database")
    return db
    
def insertDb(data, db):
    
    """Inserts current weather data into the database"""
    
    try:
        cursor = db.cursor()
        add_weather = ("INSERT INTO current_weather "
                    "(timestamp, id, main, description, temp, icon, pressure, humidity, windspeed ) "
                    "VALUES (CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s, %s)")
        cursor.execute(add_weather, data)
        db.commit()
        
    except Exception as e: 
        template = "Insert An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print(message)

def main():

    """Connects to the API and call the above functions to run the scraper"""

    url = "http://api.openweathermap.org/data/2.5/forecast?q=dublin,ie&units=metric&appid=a87a4c45fc8819c6fd6dae5a0db2439a"
    db = dbConnect()
    print("Connected!")
    
    rawData = requests.get(url)
    print(rawData.status_code)

    if rawData.status_code == 200:
        data = json.loads(rawData.text)
        print("Working")
        id = data['city']['country']
        print(id)


        # solution to missing rain data provided by Aonghus Lawlor
        data_list = data['list'][2]
        threeH_rain_predict = 0 # default is 0

        if 'rain' in data_list:                 # check for a rain prediction
            if '3h' in data_list['rain']:   # check for a 3h rain prediction
                threeH_rain_predict =  data_list['rain']['3h']



        main = data['list'][0]['weather'][0]['main']
        desc = data['list'][0]['weather'][0]['description']
        temp = data['list'][0]['main']['temp']
        icon = data['list'][0]['weather'][0]['icon']
        pressure = data['list'][0]['main']['pressure']
        humidity = data['list'][0]['main']['humidity']
        windspeed = data['list'][0]['wind']['speed']

        data = [id, main, desc, temp, icon, pressure, humidity, windspeed]
        insertDb(data, db)


    print('Job Complete')


if __name__ == "__main__":
    main()

