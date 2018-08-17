import json
import pandas as pd
import pymysql
from sqlalchemy import create_engine
from sklearn.cross_validation import train_test_split
from sklearn import metrics
import pickle
from sklearn import ensemble
from sklearn import datasets
from sklearn.utils import shuffle
from sklearn.metrics import mean_squared_error

pd.set_option('display.max_columns', 500)

with open("credentials.json") as f:
    credentials = json.loads(f.read())

host = credentials["db_host"]
user = credentials["db_user"]
password = credentials["db_pass"]
db = credentials["db_name"]

# Automate this query for every route for every direction
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:3306/{db}")
routes = pd.read_sql_query('SELECT DISTINCT lineid, direction FROM trips_2017', engine)

for index, row in routes.iterrows():
    df = pd.read_sql_query(f'SELECT * FROM trips_2017 WHERE lineid = "{row[0]}" AND direction = {row[1]}', engine)
    last_stop_on_route = pd.read_sql_query(f'SELECT max(stop_on_route) as end from combined_2017 WHERE line_id = "{row[0]}" AND direction = {row[1]}', engine)
    last_stop = last_stop_on_route['end'].iloc[0]
    
    # Replace missing actual time departure values with planned values
    df.actualtime_dep.fillna(df.plannedtime_dep, inplace=True)

    # Remove rows with missing values for actual time arrival as we cannot safely assume these are as planned
    df = df[pd.notnull(df['actualtime_arr'])]

    # Create a new column for trip duration
    df['trip_duration'] = df['actualtime_arr'] - df['actualtime_dep']

    # Create a new column with the hour of the day the trip took place
    df['actualtime_dep_H'] = round(df['actualtime_dep']/3600)

    # Hour of day of actual time arrival
    df['actualtime_arr_H'] = round(df['actualtime_arr']/3600)

    # Average hour of the day of the journey
    df['avg_H'] = (df['actualtime_dep_H'] + df['actualtime_arr_H']) / 2

    # Convert this to an integer
    df['avg_H'] = df['avg_H'].astype(int)

    # Creating column solely for the dates to correlate with the dates column on the historical weather data table
    df['time'] = df['timestamp'] + df['avg_H'] * 3600

    # Removing suppressed rows where suppressed = 1.0
    df = df.query('suppressed != 1.0')

    # Remove St. Patricks Day, because the times are going to be weird:
    df = df.query("timestamp != 1489708800")

    # Creating columns from timestamp for further processing
    df['dayofweek'] = df['timestamp']
    df['monthofyear'] = df['timestamp']

    # Converting the unix time to datetime format
    df.dayofweek = pd.to_datetime(df['dayofweek'], unit='s')
    df.monthofyear = pd.to_datetime(df['monthofyear'], unit='s')

    # Converting datetime to name of weekday, and to name of month (in separate columns)
    df['dayofweek'] = df['dayofweek'].dt.weekday_name
    df['monthofyear'] = df['monthofyear'].dt.month

    # Creating dummy variables for weekday names and name of month
    df_dayofweek_dummies = pd.get_dummies(df['dayofweek'])

    # Using data from the end of the Feb mid-term break till the start of the Easter break 
    # April was on Sunday the 16th April and the timestamps is Monday April 10th, which is the first Monday of Easter Break
    df = df.query('monthofyear == 2 or monthofyear == 3 or monthofyear == 4 and time >= 1487548800 and time < 1491782400')

    # Add day of week columns for each day
    df1 = pd.concat([df, df_dayofweek_dummies], axis=1, join_axes=[df.index])

    # Pull weather data from database
    df2 = pd.read_sql_query('SELECT * FROM DarkSky_historical_weather_data WHERE year = 2017 AND month = 3', engine)

    # Replace values for clarity purposes i.e. we care if it is cloudy; cloudy-day and cloudy-night distinctions are irrelevant
    d = {'clear-day':'clear','clear-night':'clear','partly-cloudy-day':'partly-cloudy','partly-cloudy-night':'partly-cloudy'}
    df2 = df2.replace(d)

    df2.rename(columns={'day_of_week': 'dayofweek', 'month': 'monthofyear'}, inplace=True)

    # Mergin bus and weather data on timestamp
    df3 = pd.merge(df1, df2, on=['time'])

    # Selecting 'useful' features for analysis
    features = ['avg_H', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'temp', 'precip_intensity','trip_duration']
    df3 = df3.reindex(columns=features)
    df3 = df3[features]
    df3.fillna(0, inplace=True)

    # Trip duration is in seconds, convert to minutes and round to the nearest integer
    df3['trip_duration'] = round(df3['trip_duration']/60)
    df3['trip_duration'] = df3['trip_duration'].astype(int)

    # Easier to work with whole number for temperature
    df3['temp'] = round(df3['temp'])
    df3['temp'] = df3['temp'].astype(int)

    # Our dataframe is ready for processing

    # Descriptive features
    X = df3.iloc[:, 0:10]

    # Assign data from last column to y variable
    # Target feature
    y = df3['trip_duration']

    # Fit regression model
    # Peter, maybe look at automating trying out a few different parameters and choosing the best one?
    params = {'n_estimators': 600, 'max_depth': 4, 'min_samples_split': 2,
              'learning_rate': 0.02, 'loss': 'ls'}
    gbr = ensemble.GradientBoostingRegressor(**params)
    gbr.fit(X, y)

    # Compute the importance of each feature based on the model
    pd.DataFrame({'feature': X.columns, 'importance': gbr.feature_importances_})

    # Generate predictions for the dataset
    pred = gbr.predict(X)
    predictions = pd.DataFrame(pred)
    predictions.rename(columns={0:'estimated_time'}, inplace=True)
    predictions['estimated_time'] = round(predictions['estimated_time'])
    predictions['estimated_time'] = predictions['estimated_time'].astype(int)
    predictions.head()

    # Testing for error rate > 13%
    join = pd.concat([y, predictions], axis=1)
    join['abs_error'] = abs(join['trip_duration'] - join['estimated_time'])
    mean_error = join.abs_error.mean()
    mean_trip_duration = join.trip_duration.mean()
    error_rate_percentage = (mean_error / mean_trip_duration) * 100

    pkl_filename = f"GBR_school_2017_{row[0]}_{row[1]}.pkl"
    if error_rate_percentage > 13:
        with open("/home/student/dublin_bus_project/backend/api/models/high_error_rate.txt", 'a') as w:
            w.write(f"{pkl_filename}, {error_rate_percentage},\n")

    # Storing the model trained on the full data set to a pickle file
    with open(f"/home/student/dublin_bus_project/backend/api/models/{pkl_filename}", 'wb') as file:
        pickle.dump([gbr, last_stop], file)

