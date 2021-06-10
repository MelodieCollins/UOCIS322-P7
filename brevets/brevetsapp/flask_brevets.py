"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import logging
import json
import os
import flask
from flask import Flask, redirect, url_for, request, render_template
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config
from pymongo import MongoClient

import logging
from werkzeug.exceptions import HTTPException

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()

client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.tododb

###
# Pages
###

@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')

@app.route("/display")
def display():
    return flask.render_template('display.html', items=list(db.tododb.find()))

@app.route("/someroute", methods=["GET", "POST"])
def submit():
    logging.error("request %s", request.content_type)
    js = request.get_json()
    logging.error("js %s", js)
    try:
        kms = js["km"]
        opens = js["open"]
        closes = js["close"]
        if len(kms) != len(opens) or len(kms) != len(closes):
            raise Exception("Arrays are not of equal length!")
        for km, op, cl in zip(kms, opens, closes):
            item_doc = {
                'km': km,
                'open': op,
                'close': cl
            }
            db.tododb.insert_one(item_doc)
        return flask.jsonify(a=1)
    except Exception as e:
        logging.error(e, exc_info=True)
        raise

@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response
###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    
    brevet = request.args.get('brevet', 1000, type=int)
    start = request.args.get('start')
    
    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))
    # FIXME!
    # Right now, only the current time is passed as the start time
    # and control distance is fixed to 200
    # You should get these from the webpage!
    # open_time = acp_times.open_time(km, 200, arrow.now().isoformat).format('YYYY-MM-DDTHH:mm')
    # close_time = acp_times.close_time(km, 200, arrow.now().isoformat).format('YYYY-MM-DDTHH:mm')
    
    open_time = acp_times.open_time(km, brevet, arrow.get(start, 'YYYY-MM-DDTHH:mm')).format('YYYY-MM-DDTHH:mm')
    close_time = acp_times.close_time(km, brevet, arrow.get(start, 'YYYY-MM-DDTHH:mm')).format('YYYY-MM-DDTHH:mm')
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)


#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
