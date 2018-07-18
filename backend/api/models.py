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


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class FareStages(models.Model):
    stoppointid = models.IntegerField(primary_key=True)
    stage = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fare_stages'


class Leavetimes2017(models.Model):
    dayofservice = models.CharField(max_length=30, blank=True, null=True)
    tripid = models.ForeignKey('Trips2017', models.DO_NOTHING, db_column='tripid')
    progrnumber = models.IntegerField()
    stoppointid = models.IntegerField(blank=True, null=True)
    plannedtime_arr = models.IntegerField(blank=True, null=True)
    plannedtime_dep = models.IntegerField(blank=True, null=True)
    actualtime_arr = models.IntegerField(blank=True, null=True)
    actualtime_dep = models.IntegerField(blank=True, null=True)
    vehicleid = models.IntegerField(blank=True, null=True)
    suppressed = models.IntegerField(blank=True, null=True)
    lastupdate = models.CharField(max_length=30, blank=True, null=True)
    timestamp = models.ForeignKey('Trips2017', models.DO_NOTHING, db_column='timestamp', related_name="timestamp_fk", primary_key=True)

    class Meta:
        managed = False
        db_table = 'leavetimes_2017'
        unique_together = (('timestamp', 'tripid', 'progrnumber'),)


class StaticBusData(models.Model):
    long = models.FloatField()
    lat = models.FloatField()
    longname = models.CharField(max_length=30)
    shortname = models.CharField(max_length=30)
    stoppointid = models.IntegerField(primary_key=True)
    streetname = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'static_bus_data'


class Trips2017(models.Model):
    dayofservice = models.CharField(max_length=30, blank=True, null=True)
    tripid = models.IntegerField()
    lineid = models.CharField(max_length=10, blank=True, null=True)
    routeid = models.CharField(max_length=10, blank=True, null=True)
    direction = models.IntegerField(blank=True, null=True)
    plannedtime_arr = models.IntegerField(blank=True, null=True)
    plannedtime_dep = models.IntegerField(blank=True, null=True)
    actualtime_arr = models.IntegerField(blank=True, null=True)
    actualtime_dep = models.IntegerField(blank=True, null=True)
    suppressed = models.IntegerField(blank=True, null=True)
    timestamp = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'trips_2017'
        unique_together = (('timestamp', 'tripid'),)
