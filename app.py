from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f"Welcome to the Climate App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/<start><br/>"
        f"/api/v1.0/start_date/end_date/<start>/<end>"
    )



@app.route("/api/v1.0/precipitation")
def date_prcp():
   # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return the date and PRCP data as json"""
    # Query all prcp data
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)    

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    """Return the stations"""
    results = session.query(Station.name).all()
    session.close()
    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    """Query the station with the highest number of temperature observations from last 12 months"""
    sel = [Measurement.tobs]
    results = session.query(*sel).filter(Station.station == Measurement.station).filter(Measurement.date >= '2016-08-23').filter(Station.name == 'WAIHEE 837.5, HI US').all()

    session.close()

    # Convert list of tuples into normal list
    tobs = list(np.ravel(results))

    return jsonify(tobs)

@app.route("/api/v1.0/start_date/<start_date>")
def start_date(start_date):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature
     for a given start date that matches
     the path variable supplied by the user, or a 404 if not."""

    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    dates = session.query(Measurement.date).all()
    session.close()
   
    if any(start_date in d for d in dates):
        return jsonify(f'Min Temp: {results[0][0]}F, Avg Temp: {round((results[0][1]),1)}F, Max Temp: {results[0][2]}F')

    return jsonify({"error": "Date not found."}), 404

@app.route("/api/v1.0/start_date/end_date/<start_date>/<end_date>")
def dates(start_date, end_date):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature
     for a given start and end date that matches
    the path variable supplied by the user, or a 404 if not."""

    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    dates = session.query(Measurement.date).all()
    session.close()

    if any(start_date in d for d in dates):
         if any(end_date in d for d in dates):
            return jsonify(f'Min Temp: {results[0][0]}F, Avg Temp: {round((results[0][1]),1)}F, Max Temp: {results[0][2]}F')

    return jsonify({"error": "Date not found."}), 404

if __name__ == "__main__":
    app.run(debug=True)
