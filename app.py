# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
from flask import Flask, jsonify

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

#Route for home page
@app.route('/')
def homepage():
    print("Server received request for 'Home' page...")
    return (f"Welcome to my climate app!<br/>"
            f"Available routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs"
            )

#Route for precipitation
@app.route('/api/v1.0/precipitation')
def precipitation():
    print("Server received request for 'Precipitation' page...")
    
    most_recent_date = session.query(func.max(Measurement.date)).first()
    end_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')
    start_date = end_date - dt.timedelta(days=366)
    results = session.query(Measurement.date, Measurement.prcp).filter(func.strftime(Measurement.date) >= start_date).all()

    last_12_months = []
    for date, prcp in results:
        last_12_months_dict = {}
        last_12_months_dict[date] = prcp
        last_12_months.append(last_12_months_dict)

    return jsonify(last_12_months)

#Route for stations
@app.route('/api/v1.0/stations')
def stations():
    print("Server received request for 'Stations' page...")


    results = session.query(Station.station).distinct().all()

    stations = []
    for station in results:
        stations_dict = {}
        stations_dict["station"] = station[0]
        stations.append(stations_dict)
    
    return jsonify(stations)

#Route for temperature observed
@app.route('/api/v1.0/tobs')
def tobs():
    print("Server received request for 'Temperature Observed' page...")

    most_recent_date = session.query(func.max(Measurement.date)).first()
    end_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')
    start_date = end_date - dt.timedelta(days=366)

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281')\
    .filter(func.strftime(Measurement.date) >= start_date).group_by(Measurement.date).all()

    temperatures = []
    for date, tobs in temperatures:
        temperatures_dict = {}
        temperatures_dict[date] = tobs
        temperatures.append(temperatures_dict)
    
    return jsonify(temperatures)

#Route for start date
@app.route('/api/v1.0/<start>')
def start():
    print("Server received request for 'Start' page...")

if __name__ == '__main__':
    app.run(debug = True)    