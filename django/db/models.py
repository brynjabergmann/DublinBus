# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class DarkskyCurrentWeather(models.Model):
    timestamp = models.DateTimeField(primary_key=True)
    description = models.CharField(max_length=40, blank=True, null=True)
    temp = models.FloatField(blank=True, null=True)
    icon = models.CharField(max_length=40, blank=True, null=True)
    precip_intensity = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'DarkSky_current_weather'


class DarkskyHistoricalWeatherData(models.Model):
    time = models.IntegerField(primary_key=True)
    day_of_week = models.CharField(max_length=20, blank=True, null=True)
    description = models.CharField(max_length=50, blank=True, null=True)
    temp = models.FloatField(blank=True, null=True)
    precip_intensity = models.FloatField(blank=True, null=True)
    hour = models.IntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    icon = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'DarkSky_historical_weather_data'


class DarkskyHourlyWeatherPrediction(models.Model):
    timestamp = models.DateTimeField()
    time = models.IntegerField(primary_key=True)
    day_of_week = models.CharField(max_length=10, blank=True, null=True)
    description = models.CharField(max_length=40, blank=True, null=True)
    temp = models.FloatField(blank=True, null=True)
    icon = models.CharField(max_length=40, blank=True, null=True)
    precip_intensity = models.FloatField(blank=True, null=True)
    hour = models.IntegerField(blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'DarkSky_hourly_weather_prediction'


class Leavetimes2016(models.Model):
    datasource = models.CharField(max_length=2, blank=True, null=True)
    dayofservice = models.CharField(max_length=30, blank=True, null=True)
    tripid = models.IntegerField(blank=True, null=True)
    progrnumber = models.IntegerField(blank=True, null=True)
    stoppointid = models.IntegerField(blank=True, null=True)
    plannedtime_arr = models.IntegerField(blank=True, null=True)
    plannedtime_dep = models.IntegerField(blank=True, null=True)
    actualtime_arr = models.IntegerField(blank=True, null=True)
    actualtime_dep = models.IntegerField(blank=True, null=True)
    vehicleid = models.IntegerField(blank=True, null=True)
    passengers = models.IntegerField(blank=True, null=True)
    passengersin = models.IntegerField(blank=True, null=True)
    passengersout = models.IntegerField(blank=True, null=True)
    distance = models.IntegerField(blank=True, null=True)
    suppressed = models.IntegerField(blank=True, null=True)
    justificationid = models.IntegerField(blank=True, null=True)
    lastupdate = models.CharField(max_length=30, blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'leavetimes_2016'


class Leavetimes2017(models.Model):
    datasource = models.CharField(max_length=2, blank=True, null=True)
    dayofservice = models.CharField(max_length=30, blank=True, null=True)
    tripid = models.IntegerField(blank=True, null=True)
    progrnumber = models.IntegerField(blank=True, null=True)
    stoppointid = models.IntegerField(blank=True, null=True)
    plannedtime_arr = models.IntegerField(blank=True, null=True)
    plannedtime_dep = models.IntegerField(blank=True, null=True)
    actualtime_arr = models.IntegerField(blank=True, null=True)
    actualtime_dep = models.IntegerField(blank=True, null=True)
    vehicleid = models.IntegerField(blank=True, null=True)
    passengers = models.IntegerField(blank=True, null=True)
    passengersin = models.IntegerField(blank=True, null=True)
    passengersout = models.IntegerField(blank=True, null=True)
    distance = models.IntegerField(blank=True, null=True)
    suppressed = models.IntegerField(blank=True, null=True)
    justificationid = models.IntegerField(blank=True, null=True)
    lastupdate = models.CharField(max_length=30, blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'leavetimes_2017'


class StaticBusStopData(models.Model):
    stop_id = models.IntegerField(primary_key=True)
    short_name = models.CharField(max_length=100, blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'static_bus_stop_data'


class Trips2016(models.Model):
    dayofservice = models.CharField(max_length=30, blank=True, null=True)
    tripid = models.IntegerField(blank=True, null=True)
    lineid = models.CharField(max_length=10, blank=True, null=True)
    routeid = models.CharField(max_length=10, blank=True, null=True)
    direction = models.IntegerField(blank=True, null=True)
    plannedtime_arr = models.IntegerField(blank=True, null=True)
    plannedtime_dep = models.IntegerField(blank=True, null=True)
    actualtime_arr = models.IntegerField(blank=True, null=True)
    actualtime_dep = models.IntegerField(blank=True, null=True)
    suppressed = models.IntegerField(blank=True, null=True)
    timestamp = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trips_2016'


class Trips2017(models.Model):
    dayofservice = models.CharField(max_length=30, blank=True, null=True)
    tripid = models.IntegerField(blank=True, null=True)
    lineid = models.CharField(max_length=10, blank=True, null=True)
    routeid = models.CharField(max_length=10, blank=True, null=True)
    direction = models.IntegerField(blank=True, null=True)
    plannedtime_arr = models.IntegerField(blank=True, null=True)
    plannedtime_dep = models.IntegerField(blank=True, null=True)
    actualtime_arr = models.IntegerField(blank=True, null=True)
    actualtime_dep = models.IntegerField(blank=True, null=True)
    suppressed = models.IntegerField(blank=True, null=True)
    timestamp = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trips_2017'


class Trips2017Clean(models.Model):
    dayofservice = models.CharField(max_length=30, blank=True, null=True)
    tripid = models.IntegerField(blank=True, null=True)
    lineid = models.CharField(max_length=10, blank=True, null=True)
    routeid = models.CharField(max_length=30, blank=True, null=True)
    direction = models.IntegerField(blank=True, null=True)
    actualtime_arr = models.IntegerField(blank=True, null=True)
    actualtime_dep = models.IntegerField(blank=True, null=True)
    timestamp = models.IntegerField(blank=True, null=True)
    tripduration = models.IntegerField(blank=True, null=True)
    avg_h = models.IntegerField(db_column='avg_H', blank=True, null=True)  # Field name made lowercase.
    monday = models.IntegerField(db_column='Monday', blank=True, null=True)  # Field name made lowercase.
    tuesday = models.IntegerField(db_column='Tuesday', blank=True, null=True)  # Field name made lowercase.
    wednesday = models.IntegerField(db_column='Wednesday', blank=True, null=True)  # Field name made lowercase.
    thursday = models.IntegerField(db_column='Thursday', blank=True, null=True)  # Field name made lowercase.
    friday = models.IntegerField(db_column='Friday', blank=True, null=True)  # Field name made lowercase.
    satuday = models.IntegerField(db_column='Satuday', blank=True, null=True)  # Field name made lowercase.
    sunday = models.IntegerField(db_column='Sunday', blank=True, null=True)  # Field name made lowercase.
    january = models.IntegerField(db_column='January', blank=True, null=True)  # Field name made lowercase.
    february = models.IntegerField(db_column='February', blank=True, null=True)  # Field name made lowercase.
    march = models.IntegerField(db_column='March', blank=True, null=True)  # Field name made lowercase.
    april = models.IntegerField(db_column='April', blank=True, null=True)  # Field name made lowercase.
    may = models.IntegerField(db_column='May', blank=True, null=True)  # Field name made lowercase.
    june = models.IntegerField(db_column='June', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'trips_2017_clean'
