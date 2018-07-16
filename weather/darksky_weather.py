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
            password='Team 8 Project',
            db='dublin_bus'
        )
        
    except Exception as e: 
        sys.exit("Cannot connect to database")
    return db
    
def insertDb(data, db):
    
    """Function to insert the data into the database"""
    
    try:
        cursor = db.cursor()
        
        add_weather = ("INSERT INTO DarkSky_current_weather "
                    "(timestamp, description, temp, icon, precip_intensity) "
                    "VALUES (CURRENT_TIMESTAMP, %s, %s, %s, %s)")
        
        cursor.execute(add_weather, data)
        db.commit()
        
    except Exception as e: 
        template = "Insert An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print(message)

def main():

    """Function to connect to the API and call the above functions to run the scraper"""

    url = "https://api.darksky.net/forecast/9a91b8d12a4a4a97d2c0bba6c5d18870/53.3498,-6.2603?units=si"
    db = dbConnect()
    print("Connected!")
    
    rawData = requests.get(url)
    print(rawData.status_code)

    if rawData.status_code == 200:
        data = json.loads(rawData.text)
        print("Working")
         
        description = data["currently"]["summary"]
        temp = data["currently"]["temperature"]
        icon = data["currently"]["icon"]
        rain_intensity = data["currently"]["precipIntensity"]
        
        data = [description, temp, icon, rain_intensity]
        insertDb(data, db)

             
if __name__ == "__main__":
    main()

