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

#Define route for home page
@app.route('/')
def homepage():
    print("Server received request for 'Home' page...")
    #Return available routes for the user
    return (f"Welcome to my Hawaii climate app!<br/>"
            f"Available Routes:<br/>"
            f"--------------------------------------------------------------<br/>"
            f"To see daily precipitation data for the last 12 months:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"--------------------------------------------------------------<br/>"
            f"To see a list of stations:<br/>"
            f"/api/v1.0/stations<br/>"
            f"--------------------------------------------------------------<br/>"
            f"To see the most active station's daily observed temperature for the last 12 months<br/>"
            f"/api/v1.0/tobs<br/>"
            f"--------------------------------------------------------------<br/>"
            f"Replace 'start' with a start date of your choosing (formatted YYYY-MM-DD) to see the daily minimum, average and maximum observed temperature from that date until 2017-08-23:<br/>"
            f"/api/v1.0/start<br/>"
            f"--------------------------------------------------------------<br/>"
            f"Replace 'start' and 'end' with a start and end date of your choosing (formatted YYYY-MM-DD) to see the daily minimum, average and maximum observed temperature for that range:<br/>"
            f"/api/v1.0/start/end"
            )

#Route for precipitation
@app.route('/api/v1.0/precipitation')
def precipitation():
    print("Server received request for 'Precipitation' page...")
    
    #Query Measurement and use func.max to get the most recent date, stored in a variable
    most_recent_date = session.query(func.max(Measurement.date)).first()
    #Convert to a datetime object
    end_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')
    #Use dt.timedelta to calculate the date 12 months (365 days) prior and store it in a variable
    start_date = end_date - dt.timedelta(days=366)

    #Query Measurement to get the date and the precipitation for only the last 12 months from the most recent date
    results = session.query(Measurement.date, Measurement.prcp).filter(func.strftime(Measurement.date) >= start_date).all()

    #Add results to a dictionary using a for loop and append to a list
    last_12_months = []
    for date, prcp in results:
        last_12_months_dict = {}
        last_12_months_dict[date] = prcp
        last_12_months.append(last_12_months_dict)

    #Return the jsonified list of the last 12 months of precipitation data
    return jsonify(last_12_months)

#Define route for stations
@app.route('/api/v1.0/stations')
def stations():
    print("Server received request for 'Stations' page...")

    #Query Station to get station ID and name using .distinct() to avoid duplicates
    results = session.query(Station.station, Station.name).distinct().all()

    #Add results to a dictionary using a for loop and append to a list
    stations = []
    for station, name in results:
        stations_dict = {}
        stations_dict["station"] = station
        stations_dict["name"] = name
        stations.append(stations_dict)
    
    #Returned the jsonified list of stations
    return jsonify(stations)

#Define route for temperature observed
@app.route('/api/v1.0/tobs')
def tobs():
    print("Server received request for 'Temperature Observed' page...")

    #Query Measurement and use func.max to get the most recent date, stored in a variable
    most_recent_date = session.query(func.max(Measurement.date)).first()
    #Convert to a datetime object
    end_date = dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d')
    #Use dt.timedelta to calculate the date 12 months (365 days) prior and store it in a variable
    start_date = end_date - dt.timedelta(days=366)

    #Query Measurement to get the date and temperature observed for the most active station, USC00519281
    #filtering for only the last 12 months from the most recent date, grouped by date
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281')\
    .filter(func.strftime(Measurement.date) >= start_date).group_by(Measurement.date).all()

    #Add results to a dictionary using a for loop and append to a list
    temperatures = []
    for date, tobs in results:
        temperatures_dict = {}
        temperatures_dict[date] = tobs
        temperatures.append(temperatures_dict)
    
    #Return the jsonified list of dates and temperatures
    return jsonify(temperatures)

#Define route for start date
@app.route('/api/v1.0/<start>')
def start_date(start):
    print("Server received request for 'Start' page...")

    #Query Measurement to get the min, avg and max observed temperature, filtered for dates after the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start).group_by(Measurement.date).all()
    
    #Add results to a dictionary using a for loop and append to a list
    start_tobs = []
    for tmin, tavg, tmax in results:
        start_tobs_dict = {}
        start_tobs_dict['tmin'] = tmin
        start_tobs_dict['tavg'] = tavg
        start_tobs_dict['tmax'] = tmax
        start_tobs.append(start_tobs_dict)
    
    #Return the jsonified list of min, avg and max temperatures
    return jsonify(start_tobs)

#Define route for start and end date
@app.route('/api/v1.0/<start>/<end>')
def start_and_end_date(start, end):
    print("Server received request for 'Start and End Date' page...")

    #Query Measurement to get the min, avg and max observed temperature, filtered between the start and end date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
        .filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    
    #Add results to dictionary using a for loop and append to list
    start_end_tobs = []
    for tmin, tavg, tmax in results:
        start_end_tobs_dict = {}
        start_end_tobs_dict['tmin'] = tmin
        start_end_tobs_dict['tavg'] = tavg
        start_end_tobs_dict['tmax'] = tmax
        start_end_tobs.append(start_end_tobs_dict)
    
    #Return jsonified list of min, avg and max temperatures
    return jsonify(start_end_tobs)


if __name__ == '__main__':
    app.run(debug = True)    