# Import the dependencies.



###### TO ACCESS start route DATE: /api/v1.0/start/2010-01-01  #####################################
###### TO ACCESS start/end route DATE: /api/v1.0/start_end/2010-01-01/2010-12-31  ##################


from flask import Flask, jsonify, request
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import os
import datetime as dt

app = Flask(__name__)

# Correctly generate the engine to the correct sqlite file
base_dir = os.path.abspath(os.path.dirname(__file__))
database_path = "sqlite:///" + os.path.join(base_dir, "Resources", "hawaii.sqlite")
engine = create_engine(database_path)

# Use automap_base() and reflect the database schema
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Correctly save references to the tables in the sqlite file (measurement and station)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Correctly create and bind the session between the python app and database
session = Session(engine)

@app.route('/')
def landing_page():
    # Display the available routes on the landing page
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/start/<start_date><br/>"
        "/api/v1.0/start_end/<start_date>/<end_date>"
    )

# API Static Routes

@app.route('/api/v1.0/precipitation')
def precipitation_route():
    # Returns json with the date as the key and the value as the precipitation
    # Only returns the jsonified precipitation data for the last year in the database

    # Calculate the date one year ago from the last date in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query precipitation data for the last year
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Create a dictionary with date as the key and precipitation as the value
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

@app.route('/api/v1.0/stations')
def stations_route():
    # Create a new session for each route
    session = Session(engine)

    # Query stations
    results = session.query(Station.station, Station.name).all()

    # Close the session
    session.close()

    # Convert the query results to a dictionary
    station_data = []
    for station, name in results:
        station_dict = {}
        station_dict['station'] = station
        station_dict['name'] = name
        station_data.append(station_dict)

    # Return the JSONified station data
    return jsonify(station_data)


@app.route('/api/v1.0/tobs')
def tobs_route():
    # Create a new session for each route
    session = Session(engine)
    # Returns jsonified data for the most active station (USC00519281)
    # Only returns the jsonified data for the last year of data

    # Find the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count().desc()).first()[0]

    # Calculate the date one year ago from the last date in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Query temperature data for the most active station for the last year
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station, Measurement.date >= one_year_ago).all()

    # Create a dictionary with date as the key and temperature as the value
    tobs_data = {date: tobs for date, tobs in results}

    return jsonify(tobs_data)


@app.route('/api/v1.0/start/<start_date>')
def start_route(start_date):
    # Create a new session for each route
    session = Session(engine)

    try:
        # Convert start_date to datetime object
        start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')

        # Query min, max, and avg temperatures from the given start date to the end of the dataset
        result = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start_date).all()

        # Convert the query result to a dictionary
        temp_stats = {
            'min_temp': result[0][0],
            'max_temp': result[0][1],
            'avg_temp': result[0][2]
        }

        # Return the JSONified temperature statistics
        return jsonify(temp_stats)
    except Exception as e:
        print(e)
        return jsonify({'error': 'Invalid date format or no data available.'}), 400
    finally:
        # Close the session
        session.close()

@app.route('/api/v1.0/start_end/<start_date>/<end_date>')
def start_end_route(start_date, end_date):
    # Create a new session for each route
    session = Session(engine)

    try:
        # Convert start_date and end_date to datetime objects
        start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')
        end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')

        # Query min, max, and avg temperatures from the given start date to the given end date
        result = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

        # Convert the query result to a dictionary
        temp_stats = {
            'min_temp': result[0][0],
            'max_temp': result[0][1],
            'avg_temp': result[0][2]
        }

        # Return the JSONified temperature statistics
        return jsonify(temp_stats)
    except Exception as e:
        print(e)
        return jsonify({'error': 'Invalid date format or no data available.'}), 400
    finally:
        # Close the session
        session.close()

if __name__ == "__main__":
    app.run(debug=True)