from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
#################################################
# Flask Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Station = Base.classes.station
Measurement = Base.classes.measurement
app = Flask(__name__)

#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        
    )


"""TODO: Handle API route with variable path to allow getting info
for a specific character based on their 'superhero' name """


@app.route("/api/v1.0/precipitation")
def precip_API():
    """Fetch the precipitation data"""
    session = Session(engine)#!/usr/bin/env python
    precipitation = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    pre_dict = []
    for date, pre in precipitation:
        pre_dict.append({"date":date,"precipitation":pre})
    return jsonify(pre_dict)

@app.route("/api/v1.0/stations")
def stations_API():
    """Fetch the precipitation data"""
    session = Session(engine)#!/usr/bin/env python
    stations = session.query(Station.id, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()
    station_list = []
    for ids, name, latitude, longitude, elevation in stations:
        station_dict = {}
        station_dict["id"] = ids
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        station_list.append(station_dict)
    return jsonify(station_list)
    
@app.route("/api/v1.0/tobs")
def tobs_API():
    session = Session(engine)
    date_last_year = session.query(Measurement.date).order_by(Measurement.date.desc()).all()[0][0]
    date_year_ago = dt.date.fromisoformat(date_last_year) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    data_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= date_year_ago).filter(Measurement.date<=date_last_year).all()

    session.close()
    tobs_list = []
    for date, tobs in data_tobs:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)
        
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start_API(start):
    session = Session(engine)
    start_str = f"{start}"
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= dt.date.fromisoformat(start)).all()
    session.close()
    
    temp_list = {"Start date": start, "min temperature": temps[0][0], "average temperature": temps[0][1], "max temperature": temps[0][2]}
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def startend_API(start, end):
    session = Session(engine)
    start_str = f"{start}"
    end_str  = f"{end}"
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= dt.date.fromisoformat(start)).\
    filter(Measurement.date <= dt.date.fromisoformat(end)).all()
    session.close()
    
    temp_list = {"Start date": start, "End Date": end, "min temperature": temps[0][0], "average temperature": temps[0][1], "max temperature": temps[0][2]}
    return jsonify(temp_list)
    
if __name__ == "__main__":
    app.run(debug=True)
