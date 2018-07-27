def forecast(request):

    day = dt.datetime.today().weekday()

    with connection.cursor() as cursor:
        cursor.execute("SELECT dow, hour, temp, precip_intensity from DarkSky_hourly_weather_prediction WHERE dow = %s AND hour = %s;", [day, hour])
        row = cursor.fetchone()
        dow = row[0]
        hour = row[1]
        temp = row[2]
        rain = row[3]
        forecast = { "dow" : dow, "hour" : hour, "temp" : temp, "rain" : rain }
        return JsonResponse(forecast)