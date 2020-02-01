 coding: utf-8

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
session = Session(engine)#!/usr/bin/env python
#


# # Exploratory Climate Analysis

# In[339]:


# Design a query to retrieve the last 12 months of precipitation data and plot the results

# Calculate the date 1 year ago from the last data point in the database
date_last_year = session.query(Measurement.date).order_by(Measurement.date.desc()).all()[0][0]
date_year_ago = dt.date.fromisoformat(date_last_year) - dt.timedelta(days=365)

# Perform a query to retrieve the data and precipitation scores
data_prcp = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_year_ago).filter(Measurement.date<=date_last_year).all()
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

# In[341]:


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



