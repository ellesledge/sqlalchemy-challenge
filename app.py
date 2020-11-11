import numpy as np 
import datetime as dt 
from datetime import datetime

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measure = Base.classes.measurement
Station = Base.classes.station

# Flask setup
app = Flask(__name__)

# Flask Route
@app.route("/")
def index():
    # Available routes
    return (
        f"<h2>Available Routes:</h2><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2012-04-01<br/>"
        f"/api/v1.0/2012-04-01/2012-05-01<br/>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)
    
    results = session.query(Measure.date, Measure.prcp).all()
    session.close()
    
    all_prcp = {date:prcp for date, prcp in results}
        
    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    results = session.query(Station.station, Station.name)
    session.close()
    
    all_stations = []
    for row in results:
        all_stations.append(row._asdict())  
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    last = session.query(Measure).order_by(Measure.date.desc()).first()
    clean_date = datetime.strptime(last.date, '%Y-%m-%d')
    a_year = clean_date - dt.timedelta(days=365) 
    
    pop_stat = session.query(Station.station, Station.name, func.count(Measure.station)).\
                    filter(Measure.station == Station.station).\
                    group_by(Measure.station).\
                    order_by(func.count(Measure.station).desc()).all()
    
    results = session.query(Measure.tobs).\
        filter(Measure.station == pop_stat[0][0], Measure.date>=a_year, Measure.date<=clean_date).all()
    
    session.close()
    
    all_tobs = list(np.ravel(results))
    
    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def start_temp(start):
    session = Session(engine)
    
    temp = session.query(func.min(Measure.tobs), func.max(Measure.tobs), func.avg(Measure.tobs)).\
        filter(Measure.date >= start).all()
    session.close()
    
    temp_sum = {}
    temp_sum['min_temp'] = temp[0][0]
    temp_sum['max_temp'] = temp[0][1]
    temp_sum['avg_temp'] = round(temp[0][2],1)  
    
    return jsonify(temp_sum)
 
@app.route("/api/v1.0/<start>/<end>")
def start_end_temp(start, end):
    session = Session(engine)
    
    temp = session.query(func.min(Measure.tobs), func.max(Measure.tobs), func.avg(Measure.tobs)).\
        filter(Measure.date >= start).\
        filter(Measure.date <= end).all()
    session.close()
    
    temp_sum = {}
    temp_sum['min_temp'] = temp[0][0]
    temp_sum['max_temp'] = temp[0][1]
    temp_sum['avg_temp'] = round(temp[0][2],1)
    
    return jsonify(temp_sum)
    

if __name__ == '__main__':
    app.run(debug=True)
