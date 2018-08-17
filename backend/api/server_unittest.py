from django.db import connection
import views
import unittest
import requests
import json
import views
import datetime as dt
from django.conf import settings
import django
import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.backend.settings")
#django.setup()
settings.configure()


class server_test(unittest.TestCase):

    def test_connection_weather_api(self):
        # checks if the weather API connection works"
        url = "https://api.darksky.net/forecast/9a91b8d12a4a4a97d2c0bba6c5d18870/53.3498,-6.2603"
        rawData = requests.get(url)
        self.assertTrue(rawData.status_code == 200)

    def test_city(self):
        # checks for city name of weather API data
        url = "https://api.darksky.net/forecast/9a91b8d12a4a4a97d2c0bba6c5d18870/53.3498,-6.2603"
        rawData = requests.get(url)
        data = json.loads(rawData.text)
        city = data["timezone"]
        self.assertTrue(city == "Europe/Dublin")

    def test_get_all_routes(self):
        now = dt.datetime.now().timestamp()
        paths = []
        first_stop_list = [847]
        last_stop_list = [848]

        self.assertTrue(len(views.get_all_routes(first_stop_list, last_stop_list)) == 9)



    def test_get_all_times(self):
        timings = []

    def test_get_fastest_route_index(self):
        best_route_index = 0

    def test_get_segment(self):
        hello = 0

    def test_get_direction(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT direction FROM stops_served_by_two WHERE line_id = %s AND stop_number = %s;",
                           [bus_route, bus_stop])
            direction = cursor.fetchone()[0]
            self.assertTrue(len(direction) == 1)
            self.assertLess(direction, 2)

    def test_end_to_end_prediction(self):
        days_list = [0, 0, 0, 0, 0, 0, 0]
        days_list[day_of_week] = 1

        prediction_inputs = views.end_to_end_prediction.prediction_inputs
        print(prediction_inputs)


    def test_is_school_holiday(self):
        timestamp_holiday_2018 = 1515000000
        timestamp_non_holiday_2018 = 1515369900
        timestamp_holiday_2019 = 1546300900
        timestamp_non_holiday_2019 = 1546819600

        self.assertTrue(views.is_school_holiday(timestamp_holiday_2018))
        self.assertFalse(views.is_school_holiday(timestamp_non_holiday_2018))
        self.assertTrue(views.is_school_holiday(timestamp_holiday_2019))
        self.assertFalse(views.is_school_holiday(timestamp_non_holiday_2019))


    def test_fare_finder(self):
        route = "46a"
        direction = 1
        first_stop = 264
        last_stop = 798
        num_stops = 13

        self.assertTrue(views.fare_finder(route, direction, first_stop, last_stop)["cash"] == 3.30)
        self.assertTrue(views.fare_finder(route, direction, first_stop, last_stop)["leap"] == 2.60)


    def test_chart_values(self):
        # Waiting on backend
        route = "46a"
        timestamp = dt.datetime.timestamp(dt.datetime.now())

        self.assertTrue(len(views.chart_values(route, timestamp)) == 15)


    def test_next_bus(self):
        stop_number = 264
        route = "46a"
        direction = 1
        timestamp = dt.datetime.timestamp(dt.datetime.now())

        current_year = dt.datetime.now().year
        current_month = dt.datetime.now().month
        current_day = dt.datetime.now().day
        current_weekday = dt.date.today().strftime("%A")
        # Not finished on backend so cant test


if __name__ == "__main__":
    unittest.main()













import unittest
from sqlalchemy import create_engine
import pymysql

from weather_scraper import *


class TestSetAdt(unittest.TestCase):

    def test_connection_weather_API(self):
        # checks if the weather API connection works"
        url = "http://api.openweathermap.org/data/2.5/forecast?q=dublin,ie&units=metric&appid=a87a4c45fc8819c6fd6dae5a0db2439a"
        rawData = requests.get(url)
        self.assertTrue(rawData.status_code == 200)

    def test_city(self):
        # checks for city name of API data
        url = "http://api.openweathermap.org/data/2.5/forecast?q=dublin,ie&units=metric&appid=a87a4c45fc8819c6fd6dae5a0db2439a"
        rawData = requests.get(url)
        data = json.loads(rawData.text)
        city = data['city']['name']
        self.assertTrue(city == "Dublin")

    def test_connection_JCDecaux_API(self):
        # checks if the JCDecaux API connection works"
        url = 'https://api.jcdecaux.com/vls/v1/stations?contract=Dublin&apiKey=163a27dc14a77d825fb26c4212d74477642b4469'  # the website containing the data
        web_data = requests.get(url)
        self.assertTrue(web_data.status_code == 200)

    def test_query(self):
        # testing query returns correct output and DB connection
        stations = []
        engine = create_engine("mysql+pymysql://publicdb:sqlpublic@52.43.48.163:3306/sqlpublic", echo=False)
        connection = engine.connect()
        trans = connection.begin()
        rows = connection.execute("Select distinct(lat),lng from bikes where address = 'Bolton Street'")
        trans.commit()
        for i in rows:
            stations.append(dict(i))
        self.assertTrue(stations == [{'lat': 53.3512, 'lng': -6.269859}])

    def test_query_2(self):
        # testing query returns correct output and DB connection
        weather_id = []
        engine = create_engine("mysql+pymysql://publicdb:sqlpublic@52.43.48.163:3306/sqlpublic", echo=False)
        connection = engine.connect()
        trans = connection.begin()
        rows = connection.execute("SELECT id FROM weather")
        trans.commit()
        for i in rows:
            weather_id.append(dict(i))
        self.assertTrue(weather_id == [{'id': "IE"}])

    def test_query3(self):
        # testing query for station names with special characters - apostrophe;'s
        stations = []
        engine = create_engine("mysql+pymysql://publicdb:sqlpublic@52.43.48.163:3306/sqlpublic", echo=False)
        connection = engine.connect()
        trans = connection.begin()
        rows = connection.execute("Select distinct(lat),lng from bikes where address = 'Georges's Lane'")
        trans.commit()
        for i in rows:
            stations.append(dict(i))
        self.assertTrue(stations == [{'lat': 53.3502, 'lng': -6.279696}])

        # solution

    def test_query4(self):
        # testing query for station names with special characters - apostrophe;'s
        stations = []
        engine = create_engine("mysql+pymysql://publicdb:sqlpublic@52.43.48.163:3306/sqlpublic", echo=False)
        connection = engine.connect()
        trans = connection.begin()
        rows = connection.execute(
            "Select distinct(lat),lng from bikes where address = 'George''s Lane'")  # Query only works if the apostrophe is doubled up.
        trans.commit()
        for i in rows:
            stations.append(dict(i))
        self.assertTrue(stations == [{'lat': 53.3502, 'lng': -6.279696}])

    def test_query5(self):
        # testing query for station names with special characters - forward slash
        stations = []
        engine = create_engine("mysql+pymysql://publicdb:sqlpublic@52.43.48.163:3306/sqlpublic", echo=False)
        connection = engine.connect()
        trans = connection.begin()
        rows = connection.execute(
            "Select distinct(lat),lng from bikes where address = 'Princes Street / O'Connell Street'")
        trans.commit()
        for i in rows:
            stations.append(dict(i))
        self.assertTrue(stations == [{'lat': 53.349, 'lng': -6.260311}])

    # solution
    def test_query6(self):
        # testing query for station names with special characters - forward slash
        stations = []
        engine = create_engine("mysql+pymysql://publicdb:sqlpublic@52.43.48.163:3306/sqlpublic", echo=False)
        connection = engine.connect()
        trans = connection.begin()
        rows = connection.execute(
            "Select distinct(lat),lng from bikes where address = 'Princes Street \/ O''Connell Street'")  # Both the slash and the apostrophe need to be escaped for this to work
        trans.commit()
        for i in rows:
            stations.append(dict(i))
        self.assertTrue(stations == [{'lat': 53.349, 'lng': -6.260311}])


if _name_ == "_main_":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestSetAdt)
    unittest.TextTestRunner().run(suite)