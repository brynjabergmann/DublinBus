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

host = credentials["host"]
user = credentials["db_user"]
password = credentials["db_pass"]
db = credentials["db_name"]

# Automate this query for every route for every direction
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:3306/{db}")
routes = pd.read_sql_query('SELECT DISTINCT lineid, direction FROM trips_2017', engine)

for index, row in routes.iterrows():
    df = pd.read_sql_query(f'SELECT * FROM trips_2017 WHERE lineid = "{row[0]}" AND direction = {row[1]}', engine)

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

    # Removing rows not in the month of March
    # We chose March as we felt it was the best representation of a typical 'school' month
    df = df.query('monthofyear == 3')


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

    # Peter, if this is more than 9, maybe get the script to flag this pickle, possible with the file name?
    if metrics.mean_absolute_error(y, predictions) > 9:
        pkl_filename = f"GBR_March_2017_{row[0]}_{row[1]}_HIGH-ERROR.pkl"
    else:
        pkl_filename = f"GBR_March_2017_{row[0]}_{row[1]}.pkl"

    # Storing the model trained on the full data set to a pickle file
    with open(f"models/{pkl_filename}", 'wb') as file:
        pickle.dump(gbr, file)

