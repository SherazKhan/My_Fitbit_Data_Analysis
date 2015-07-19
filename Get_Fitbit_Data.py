#!/usr/bin/env python

'''
Python script to use python-fitbit library to access Fitbit API for my personal 
Fitbit data. This code updates Daily summary data and intraday data csv files by getting the 
latest data (after previous log) from the API.

Link to the python-fitbit client API that I use: https://github.com/orcasgit/python-fitbit

Author: Manish Kurse
Created: 28 June 2015
Last modified: 28 June 2015
'''

import fitbit
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
import csv
import sys, os
from collections import deque

def get_latest_fitbit_data(authd_client, last_log_date, yesterday):
    
    last_log_date_str = datetime.strftime(last_log_date,"%Y-%m-%d")
    yesterday_str = datetime.strftime(yesterday,"%Y-%m-%d")
    
    # Retrieve time series data by accessing Fitbit API. 
    # Note that the last logged date is the first date because data only upto yesterday gets written into csv.
    # Today is not over, hence incomplete data from today is not logged.

    steps = authd_client.time_series('activities/steps', base_date= last_log_date_str ,end_date=yesterday_str)
    cals = authd_client.time_series('activities/calories', base_date= last_log_date_str ,end_date=yesterday_str)
    dist = authd_client.time_series('activities/distance', base_date= last_log_date_str ,end_date=yesterday_str)
    floors = authd_client.time_series('activities/floors', base_date= last_log_date_str ,end_date=yesterday_str)
    sedant = authd_client.time_series('activities/minutesSedentary', base_date= last_log_date_str ,end_date=yesterday_str)
    elevation = authd_client.time_series('activities/elevation', base_date= last_log_date_str ,end_date=yesterday_str)
    active_light = authd_client.time_series('activities/minutesLightlyActive', base_date= last_log_date_str ,end_date=yesterday_str)
    active_fair = authd_client.time_series('activities/minutesFairlyActive', base_date= last_log_date_str ,end_date=yesterday_str)
    active_very = authd_client.time_series('activities/minutesVeryActive', base_date= last_log_date_str ,end_date=yesterday_str)
    active_cals = authd_client.time_series('activities/activityCalories', base_date= last_log_date_str ,end_date=yesterday_str)
    sleep_start = authd_client.time_series('sleep/startTime', base_date= last_log_date_str ,end_date=yesterday_str)
    sleep_timeInBed = authd_client.time_series('sleep/timeInBed', base_date= last_log_date_str ,end_date=yesterday_str)
    sleep_minutesAsleep = authd_client.time_series('sleep/minutesAsleep', base_date= last_log_date_str ,end_date=yesterday_str)
    sleep_awakeningsCount = authd_client.time_series('sleep/awakeningsCount', base_date= last_log_date_str ,end_date=yesterday_str)
    sleep_minutesAwake = authd_client.time_series('sleep/minutesAwake', base_date= last_log_date_str ,end_date=yesterday_str)
    sleep_minutesToFallAsleep = authd_client.time_series('sleep/minutesToFallAsleep', base_date= last_log_date_str ,end_date=yesterday_str)
    sleep_minutesAfterWakeup = authd_client.time_series('sleep/minutesAfterWakeup', base_date= last_log_date_str ,end_date=yesterday_str)
    sleep_efficiency = authd_client.time_series('sleep/efficiency', base_date= last_log_date_str ,end_date=yesterday_str)

    df = pd.DataFrame()
    num_days = yesterday - last_log_date + timedelta(1)
    date_list = [last_log_date.date() + timedelta(days=x) for x in range(0, num_days.days)]
    df['date'] = date_list
    df['calories'] = pd.DataFrame(cals['activities-calories'])['value'].astype(int)
    df['steps'] = pd.DataFrame(steps['activities-steps'])['value'].astype(int)
    df['dist'] = pd.DataFrame(dist['activities-distance'])['value'].astype(float)
    df['floors'] = pd.DataFrame(floors['activities-floors'])['value'].astype(int)
    df['elevation'] = pd.DataFrame(elevation['activities-elevation'])['value'].astype(float)
    df['sedant'] = pd.DataFrame(sedant['activities-minutesSedentary'])['value'].astype(int)
    df['active_light'] = pd.DataFrame(active_light['activities-minutesLightlyActive'])['value'].astype(int)
    df['active_fair'] = pd.DataFrame(active_fair['activities-minutesFairlyActive'])['value'].astype(int)
    df['active_very'] = pd.DataFrame(active_very['activities-minutesVeryActive'])['value'].astype(int)
    df['active_cals'] = pd.DataFrame(active_cals['activities-activityCalories'])['value'].astype(int)
    df['sleep_start'] = pd.DataFrame(sleep_start['sleep-startTime'])['value']
    df['sleep_timeInBed'] = pd.DataFrame(sleep_timeInBed['sleep-timeInBed'])['value'].astype(int)
    df['sleep_minutesAsleep'] = pd.DataFrame(sleep_minutesAsleep['sleep-minutesAsleep'])['value'].astype(int)
    df['sleep_awakeningsCount'] = pd.DataFrame(sleep_awakeningsCount['sleep-awakeningsCount'])['value'].astype(int)
    df['sleep_minutesAwake'] = pd.DataFrame(sleep_minutesAwake['sleep-minutesAwake'])['value'].astype(int)
    df['sleep_minutesToFallAsleep'] = pd.DataFrame(sleep_minutesToFallAsleep['sleep-minutesToFallAsleep'])['value'].astype(int)
    df['sleep_minutesAfterWakeup'] = pd.DataFrame(sleep_minutesAfterWakeup['sleep-minutesAfterWakeup'])['value'].astype(int)
    df['sleep_efficiency'] = pd.DataFrame(sleep_efficiency['sleep-efficiency'])['value'].astype(int)
    return df

def write_fitbit_data_to_csv(df,data_filename,log_filename):
    # Write the data frame to csv.
    with open(data_filename, 'a') as f:
        df.to_csv(f, header=False,index = False)

    # Log current date as the date last logged.
    today = datetime.today()
    today_str = datetime.strftime(today,"%Y-%m-%d")

    with open(log_filename,'ab') as csvfile:
        csvwrite = csv.writer(csvfile, delimiter=',')
        csvwrite.writerow(['Data last logged',today_str])
        
        
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n) 

def get_intraday_data(authd_client,authd_client2,start_date,end_date):
    rate_limit = 150
    df_master = pd.DataFrame()
    
    num_days = end_date - start_date
    
    # If the number of calls is going to exceed the rate limit, then change end date to last feasible date
    if num_days.days > int((rate_limit-18)/7):
        end_date = start_date + timedelta(int((rate_limit-18)/7))
        print('Date range causes rate limit to exceed')
    else:
        try:
            for single_date in daterange(start_date, end_date+timedelta(1)):
                # Create a separate dataframe for intra day data
                
                df_intra = pd.DataFrame(columns=['time_intra','steps_intra','calories_intra','distance_intra'\
                                                 'elevation_intra','floors_intra','date'])
                df_hr_intra = pd.DataFrame(columns=['time_intra','hr_intra'])
                df_sleep_intra = pd.DataFrame(columns=['time_intra','sleep_intra'])

                # Get intra day data using oauth client
                steps_intra = authd_client.intraday_time_series('activities/steps',base_date=single_date)
                calories_intra = authd_client.intraday_time_series('activities/calories',base_date=single_date)
                distance_intra = authd_client.intraday_time_series('activities/distance',base_date=single_date)
                elevation_intra = authd_client.intraday_time_series('activities/elevation',base_date=single_date)
                floors_intra = authd_client.intraday_time_series('activities/floors',base_date=single_date)

                # Intra sleep data
                sleep_intra = authd_client.get_sleep(single_date)

                # Heart rate using oauth2.0
                try:
                    hr_intra = authd_client2.intraday_time_series('activities/heart',base_date=single_date)
                except fitbit.exceptions.HTTPUnauthorized:
                    print('Please provide latest refresh and access tokens for oauth2. Exiting program.')
                    sys.exit(1)
                    
                # Temporary pandas dataframes hold all the data before being merged to one big dataframe
                df_intra['time_intra'] = pd.DataFrame(steps_intra['activities-steps-intraday']['dataset'])['time']
                df_intra['steps_intra'] = pd.DataFrame(steps_intra['activities-steps-intraday']['dataset'])['value'].astype(int)
                df_intra['calories_intra'] = pd.DataFrame(calories_intra['activities-calories-intraday']['dataset'])['value'].astype(int)
                df_intra['distance_intra'] = pd.DataFrame(distance_intra['activities-distance-intraday']['dataset'])['value'].astype(float)
                df_intra['elevation_intra'] = pd.DataFrame(elevation_intra['activities-elevation-intraday']['dataset'])['value'].astype(float)
                df_intra['floors_intra'] = pd.DataFrame(floors_intra['activities-floors-intraday']['dataset'])['value'].astype(int)
                df_intra['date'] = single_date.date()
                df_hr_intra['time_intra'] = pd.DataFrame(hr_intra['activities-heart-intraday']['dataset'])['time']
                df_hr_intra['hr_intra'] = pd.DataFrame(hr_intra['activities-heart-intraday']['dataset'])['value'].astype(int)

                # Some days don't have sleep information if Fitbit was not worn before going to bed (or for other reasons)
                if not sleep_intra['sleep']:
                    print (['No sleep data for ',str(datetime.strftime(single_date,"%Y-%m-%d"))])
                else:
                    df_sleep_intra['time_intra'] = pd.DataFrame(sleep_intra['sleep'][0]['minuteData'])['dateTime']
                    df_sleep_intra['sleep_intra'] = pd.DataFrame(sleep_intra['sleep'][0]['minuteData'])['value'].astype(int)

                # Merge the two data frames into one. Note the reason for doing it this way is because the heart rate data does not necessarily 
                # have all the minutes. Whenever the Fitbit has been removed and kept aside, no HR data was collected 
                df_intra = pd.merge(df_intra,df_hr_intra, how='left', on='time_intra',
                      left_index=False, right_index=False, sort=False,
                      suffixes=('_x', '_y'), copy=True)

                df_intra = pd.merge(df_intra,df_sleep_intra, how='left', on='time_intra',
                      left_index=False, right_index=False, sort=False,
                      suffixes=('_x', '_y'), copy=True)

                # Concatenate to master dataframe
                df_master = pd.concat([df_master,df_intra], ignore_index = True)
        except fitbit.exceptions.HTTPTooManyRequests:
            print('Rate limit reached. Rerun program after 1 hour. Exiting program.')
            sys.exit(1)
            
    return df_master


#-------------------------
# MAIN SCRIPT

# Get Fitbit User keys and secrets from csv file
auth_keys = dict()
with open('Data/access_tokens.csv','r') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',')
    for row in csv_reader:
        auth_keys[row[0]] = row[1]

# Create an oauth and oauth2 client 
authd_client = fitbit.Fitbit(auth_keys['consumer_key'], auth_keys['consumer_secret'], resource_owner_key =auth_keys['user_key'], resource_owner_secret =auth_keys['user_secret'])
authd_client2 = fitbit.Fitbit(auth_keys['client_id'], auth_keys['client_secret'], oauth2=True, access_token=auth_keys['access_token'], refresh_token=auth_keys['refresh_token'])

# Read log file to find out the last day Fitbit data was logged
with open('Data/Data_log_dates.csv') as csvfile:
    temp = deque(csv.reader(csvfile), 1)[0]

# Get yesterday's date and last logged date in both datetime format and in string format
# Data from today is incomplete and not logged. So we are interested in yesterday's date.

last_log_date = datetime.strptime(temp[1],"%Y-%m-%d")
today = datetime.today()
yesterday = today - timedelta(days=1) 

# Get latest fitbit daily data
df = get_latest_fitbit_data(authd_client,last_log_date,yesterday)

# Add latest daily data to daily data csv file
write_fitbit_data_to_csv(df,'Data/Daily_Fitbit_Data.csv','Data/Data_log_dates.csv')

# Get latest intraday data
# Read log file to find out the last day Fitbit data was logged
with open('Data/Data_log_dates_intraday.csv') as csvfile:
    temp = deque(csv.reader(csvfile), 1)[0]
last_log_date = datetime.strptime(temp[1],"%Y-%m-%d")

# Get intraday data for all days from last_log_date to yesterday
df_master = get_intraday_data(authd_client,authd_client2,last_log_date,yesterday)

# Add latest daily intra day data to daily data csv file
write_fitbit_data_to_csv(df_master,'Data/Intraday_data.csv','Data/Data_log_dates_intraday.csv')

