import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#Access the SQLite database.
engine = create_engine("sqlite:///hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

app = Flask(__name__)
#define the welcome route
@app.route('/')
#create a function
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')

#create the route - precipitation
@app.route("/api/v1.0/precipitation")
#create the precipitation function
def precipitation():
    # Calculate the date one year from the last date in data set.
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
    precip = {date: prcp for date, prcp in precipitation}
    #jsonify() to format our results into a JSON structured file
    return jsonify(precip)

#create the route - stations
@app.route("/api/v1.0/stations")
#create the stations function
def stations():
    ## How many stations are available in this dataset
    results = session.query(Station.station).all()
    #function 'np.ravel()' with 'results' as our parameter to unraveling our results into a one-dimensional array
    #and convert our unraveled results into a list
    #Then jsonify the list and return it as JSON
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

#create the route - temperature oibservations route
@app.route("/api/v1.0/tobs")
#create the function
def temp_monthly():
    # Calculate the date one year from the last date in data set.
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Choose the station with the highest number of temperature observations.
    # Query the last 12 months of temperature observation data for this station
    results = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= prev_year).all() 
    #function 'np.ravel()' with 'results' as our parameter to unraveling our results into a one-dimensional array
    #and convert our unraveled results into a list
    #Then jsonify the list and return it as JSON
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

#create the route - min,avg,max temperature. provide start and ending date
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
#create the function
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        #asterisk is used to indicate there will be multiple results for our query: minimum, average, and maximum temperatures
        results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)