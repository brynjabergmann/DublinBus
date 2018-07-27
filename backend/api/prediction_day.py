import pandas as pd
import json
import pymysql
import datetime as dt
from sqlalchemy import create_engine
import pickle
import csv


pd.set_option('display.max_columns', 500)
with open("credentials.json") as f:
    credentials = json.loads(f.read())

host = credentials["db_host"]
user = credentials["db_user"]
password = credentials["db_pass"]
db = credentials["db_name"]

day = dt.datetime.today().weekday()

engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:3306/{db}")
for hour in range(24):
    weather_forecast = pd.read_sql_query(f"SELECT dow, hour, temp, precip_intensity from DarkSky_hourly_weather_prediction WHERE dow = {day} AND hour = {hour}", engine)

    days_list = [0, 0, 0, 0, 0, 0, 0]
    days_list[weather_forecast.iat[0, 0]] = 1

    # Create a pandas dataframe to be fed into the prediction model
    prediction_inputs = pd.DataFrame({
        "avg_H": [weather_forecast.iloc[0]['hour']],
        "DOW_Monday": [days_list[0]],
        "DOW_Tuesday": [days_list[1]],
        "DOW_Wednesday": [days_list[2]],
        "DOW_Thursday": [days_list[3]],
        "DOW_Friday": [days_list[4]],
        "DOW_Saturday": [days_list[5]],
        "DOW_Sunday": [days_list[6]],
        "temp": [weather_forecast.iloc[0]['temp']],
        "precip_intensity": [weather_forecast.iloc[0]['precip_intensity']]
    })

    with open("models/GBR_March_2017_46A_1.pkl", "rb") as f:
        cucumber = pickle.load(f)

    model = cucumber[0]
    max_stops = cucumber[1]

    end_to_end = int(round(model.predict(prediction_inputs)[0]))  # Predict time from start to finish

    #print(day, hour, end_to_end)
    with open("output_day.csv", 'a', newline='') as w:
        writer = csv.writer(w)
        writer.writerow([day, hour, end_to_end])

