#!/usr/bin/env python
# coding: utf-8

# In[70]:


get_ipython().run_line_magic('matplotlib', 'inline')
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt


# In[2]:


import numpy as np
import pandas as pd


# In[3]:


import datetime as dt


# # Reflect Tables into SQLAlchemy ORM

# In[20]:


# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect


# In[21]:


engine = create_engine("sqlite:///Resources/hawaii.sqlite")
engine.execute("select * from Measurement LIMIT 5").fetchall()


# In[89]:


inspector = inspect(engine)
columns = inspector.get_columns('station')
for c in columns:
    print(c['name'], c["type"])


# In[23]:


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)


# In[24]:


# We can view all of the classes that automap found
Base.classes.keys()


# In[25]:


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# In[26]:


# Create our session (link) from Python to the DB
session = Session(engine)


# # Exploratory Climate Analysis

# In[339]:


# Design a query to retrieve the last 12 months of precipitation data and plot the results

# Calculate the date 1 year ago from the last data point in the database
date_last_year = session.query(Measurement.date).order_by(Measurement.date.desc()).all()[0][0]
date_year_ago = dt.date.fromisoformat(date_last_year) - dt.timedelta(days=365)

# Perform a query to retrieve the data and precipitation scores
data_prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_year_ago).filter(Measurement.date<=date_last_year).all()
# Save the query results as a Pandas DataFrame and set the index to the date column
prcp_df = pd.DataFrame(data_prcp)
prcp_df = prcp_df.set_index('date')
# Sort the dataframe by date
prcp_df = prcp_df.sort_values("date")
# Use Pandas Plotting with Matplotlib to plot the data
plt.plot(prcp_df)
plt.title("Precipitation For Past Year in Hawaii by Date")
plt.ylabel("Precipitation (in.)")
plt.xlabel(f"Date ({date_year_ago} to {date_last_year})")


# ![precipitation](Images/precipitation.png)

# In[340]:


# Use Pandas to calcualte the summary statistics for the precipitation data
prcp_df.describe()


# ![describe](Images/describe.png)

# In[96]:


# Design a query to show how many stations are available in this dataset?
count_stations = session.query(func.count(Station.station)).all()[0][0]
print(count_stations)


# In[111]:


# What are the most active stations? (i.e. what stations have the most rows)?
# List the stations and the counts in descending order.
active_stations = session.query(Measurement.station, func.count(Measurement.id)).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).all()
print(active_stations)


# In[118]:


# Using the station id from the previous query, calculate the lowest temperature recorded, 
# highest temperature recorded, and average temperature of the most active station?
lowest_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.station == active_stations[0][0]).all()[0][0]
highest_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.station == active_stations[0][0]).all()[0][0]
average_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.station == active_stations[0][0]).all()[0][0]
print(f"{lowest_temp}, {highest_temp}, {average_temp}")


# In[162]:


# Choose the station with the highest number of temperature observations.
# Query the last 12 months of temperature observation data for this station and plot the results as a histogram
temps = session.query(Measurement.tobs).filter(Measurement.station == active_stations[0][0], Measurement.date > date_year_ago).all()
temps = pd.DataFrame(temps)
plt.hist(temps["tobs"], bins = 12, label="tobs")
plt.ylabel("Frequency")
plt.legend(loc="upper left")


# ![precipitation](Images/station-histogram.png)

# In[161]:


# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """

    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

# function usage example
print(calc_temps('2012-02-28', '2012-03-05'))


# In[341]:


# Use your previous function `calc_temps` to calculate the tmin, tavg, and tmax 
# for your trip using the previous year's data for those same dates.
cal_temp = calc_temps('2017-02-28','2017-03-05')
print(cal_temp)


# In[342]:


# Plot the results from your previous query as a bar chart. 
# Use "Trip Avg Temp" as your Title
# Use the average temperature for the y value
# Use the peak-to-peak (tmax-tmin) value as the y error bar (yerr)

plt.figure(figsize=(3, 6))
plt.bar(x=0.05,height=cal_temp[0][1], yerr = cal_temp[0][2] - cal_temp[0][0], width =0.1, align ='edge', alpha=0.5)
plt.grid(axis= 'x')
plt.ylabel("Temp (F)")
plt.title("Trip Avg Temp")
plt.xlim(0,0.20)
plt.xticks([])


# In[377]:


# Calculate the total amount of rainfall per weather station for your trip dates using the previous year's matching dates.
# Sort this in descending order by precipitation amount and list the station, name, latitude, longitude, and elevation

session.query(Measurement.station, Station.name, Station.latitude, Station.longitude, Station.elevation, func.sum(Measurement.prcp)).filter(Measurement.station == Station.station).filter(Measurement.date > '2017-02-28').filter(Measurement.date < '2017-03-05').group_by(Measurement.station).order_by(func.sum(Measurement.prcp).desc()).all()


# ## Optional Challenge Assignment

# In[344]:


# Create a query that will calculate the daily normals 
# (i.e. the averages for tmin, tmax, and tavg for all historic data matching a specific month and day)

def daily_normals(date):
    """Daily Normals.
    
    Args:
        date (str): A date string in the format '%m-%d'
        
    Returns:
        A list of tuples containing the daily normals, tmin, tavg, and tmax
    
    """
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    return session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) == date).all()
    
daily_normals("01-01")


# In[440]:


# calculate the daily normals for your trip
# push each tuple of calculations into a list called `normals`

# Set the start and end date of the trip
dt_st = "2018-02-28"
dt_end = "2018-03-05"
# Use the start and end date to create a range of dates
dte = dt_st
dt_range = []
while dt.date.fromisoformat(dte) <= dt.date.fromisoformat(dt_end):
    dt_range.append(dt.date.fromisoformat(dte))
    dte = dt.date.isoformat(dt.date.fromisoformat(dte) + dt.timedelta(days=1))
# Stip off the year and save a list of %m-%d strings
dt_range_md = [dtf.strftime("%m-%d") for dtf in dt_range]
dt_range_md
# Loop through the list of %m-%d strings and calculate the normals for each date
normals = [daily_normals(dtr) for dtr in dt_range_md]
normals  
trip_dates = [dtf.strftime("%Y-%m-%d") for dtf in dt_range]
normals = [normals[i][0] for i in range(0,len(normals))]
trip_df = pd.DataFrame(normals, columns = ["tmin", "tave", "tmax"])
trip_dates
trip_df["date"] = trip_dates
trip_df.set_index("date")


# In[22]:


# Load the previous query results into a Pandas DataFrame and add the `trip_dates` range as the `date` index


# In[462]:


# Plot the daily normals as an area plot with `stacked=False`
plt.plot(trip_df["date"], trip_df["tmin"], alpha=0.2)
plt.fill_between(trip_df["date"], trip_df["tmin"], alpha=0.2, label="tmin")
plt.plot(trip_df["date"], trip_df["tave"], alpha  = 0.2)
plt.fill_between(trip_df["date"], trip_df["tave"], alpha=0.2, label="tave")
plt.plot(trip_df["date"],trip_df["tmax"], alpha = 0.2)
plt.fill_between(trip_df["date"], trip_df["tmax"], alpha=0.2, label ="tmax")
plt.xticks(rotation=45)
plt.legend()


# In[ ]:




