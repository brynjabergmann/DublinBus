import time
import calendar
import requests
import json
import time 
import pymysql
import pandas as pd
from pymysql.err import IntegrityError
from time import sleep, strftime, gmtime
import pymysql.cursors
import datetime
import sys

def dbConnect():
    
    """Function to connect to the database"""
    
    try:
        db = pymysql.connect(
            host='localhost',
            user='superfint',
            passwd='Team 8 Project',
            db='dublin_bus'
        )
        
    except Exception as e: 
        sys.exit("Cannot connect to database")
    return db
    
def insertDb(data, db):
    
    """Function to insert the data into the database"""
    
    try:
        cursor = db.cursor()
            
        add_weather = (" INSERT INTO DarkSky_hourly_weather_prediction "
                    "(timestamp, time, day_of_week, description, temp, icon, precip_intensity, hour, month, date, dow) "
                    "VALUES (CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        
        cursor.execute(add_weather, data)
        db.commit()
        
    except Exception as e: 
        template = "While trying to insert into the table, an exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print(message)    
        
def truncateDb(db):
    
    """Function to truncate the data from the database"""
    
    try:
        cursor = db.cursor()
        truncate = (" TRUNCATE TABLE DarkSky_hourly_weather_prediction ")
        cursor.execute(truncate)
        db.commit()
        
    except Exception as e: 
        template = "While trying to truncate the table, an exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print(message)    
        
def main():

    """Function to connect to the API and call the above functions to run the scraper"""

    url = "https://api.darksky.net/forecast/9a91b8d12a4a4a97d2c0bba6c5d18870/53.3498,-6.2603?units=si&extend=hourly&exclude=daily,flags,minutely"
    db = dbConnect()
    print("Connected!")
    
    rawData = requests.get(url)
    print(rawData.status_code)

    if rawData.status_code == 200:
        data = json.loads(rawData.text)
        print("Working")
        
        truncateDb(db)
         
        for i in range(168):
            time = data["hourly"]["data"][i]["time"]
            description = data["hourly"]["data"][i]["summary"]
            temp = data["hourly"]["data"][i]["temperature"]
            icon = data["hourly"]["data"][i]["icon"]
            precip_intensity = data["hourly"]["data"][i]["precipIntensity"]
            date = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
            month = datetime.datetime.fromtimestamp(time).strftime('%m')
            hour = datetime.datetime.fromtimestamp(time).strftime('%H')
            day_of_week = calendar.day_name[datetime.datetime.fromtimestamp(time).weekday()]
            dow = datetime.datetime.today().weekday()

            data[i] = [time, day_of_week, description, temp, icon, precip_intensity, hour, month, date, dow]
            insertDb(data[i], db)
    
    print("Finished!")
           
if __name__ == "__main__":
    main()
