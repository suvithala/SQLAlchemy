import datetime as dt
import numpy as np
import pandas as pd
import json

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


############################################################################################
# Database Setup
############################################################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurements
Station = Base.classes.stations

# Create our session (link) from Python to the DB
session = Session(engine)

############################################################################################
# Flask Setup
############################################################################################
app = Flask(__name__)



############################################################################################
# Flask Routes
############################################################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Avalable Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/startend<br/>"

    )

############################################################################################
# Query for the dates and precipitation observations from the last year.
# Convert the query results to a Dictionary using date as the key and tobs as the value.
# Return the json representation of your dictionary.
#############################################################################################

@app.route("/precipitation")

def prcp():
    results = session.query(Measurement.date,Measurement.prcp).\
                    filter(Measurement.date >= '2017-01-01', Measurement.date <= '2017-12-31').\
                    group_by(Measurement.date).\
                    order_by(Measurement.date).all()

	#Create a dictionary from the row data and append to a list of precipdata
    precipdata = []
    for result in results:
        row = {}
        row["date"] = result[0]
        row["prcp"] = float(result[1])
        precipdata.append(row)

    return jsonify(precipdata)

############################################################################################
# jason list of stations
#############################################################################################

@app.route("/stations")

def stations():
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    stationlist = list(np.ravel(results))

    return jsonify(stationlist)

############################################################################################
# jason list of temperature observations from previous year
#############################################################################################

@app.route("/tobs")

def obs():
	results = session.query(Measurement.tobs).\
                    filter(Measurement.date >= '2017-01-01', Measurement.date <= '2017-12-31').all()
	tobslist = np.ravel(results)
	return jsonify(tobslist.tolist())


############################################################################################
#json list of the minimum temperature, the average temperature, and the max temperature 
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and 
#equal to the start date.
#############################################################################################

@app.route("/start")

def startdate():
	startdt = '2017-07-01'
	temp_data = session.query(func.max(Measurement.tobs),func.avg(Measurement.tobs),func.min(Measurement.tobs)).\
                        filter(Measurement.date >= startdt).all()
	startdata = []
	for result in temp_data:
		row = {}
		row["TMAX"] = str(result[0])
		row["TAVG"] = float(result[1])
		row["TMIN"] = str(result[2])
		startdata.append(row)

	return jsonify(startdata)


############################################################################################
#Return a json list of the minimum temperature, the average temperature, and the max 
#temperature for a given start or start-end range. When given the start and the end date, 
#calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
#############################################################################################

@app.route("/startend")

def startenddate():
	startdt = '2017-01-01'
	enddt = '2017-12-31'
	results = session.query(func.max(Measurement.tobs), func.avg(Measurement.tobs),func.min(Measurement.tobs)).\
                        filter(Measurement.date >= startdt, Measurement.date <= enddt,).all()
	startenddata = []
	for result in results:
		row = {}
		row["TMAX"] = str(result[0])
		row["TAVG"] = float(result[1])
		row["TMIN"] = str(result[2])
		startenddata.append(row)


	return jsonify(startenddata)


if __name__ == '__main__':
    app.run() 