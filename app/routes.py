import csv
from datetime import datetime as datetime
import os.path
import subprocess
import pandas as pd
from flask import jsonify, request, session
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask import render_template,redirect
from flask import current_app as app
from flask import render_template, request
import threading

from . import app, jwt
from config.config import Config
from pymongo import MongoClient

app.config.from_object(Config)


uri ="mongodb://localhost:27017/"
client = MongoClient(uri)
database = client['cpcpkdb']
collection_2 = client.configurationfiles
summary_collection = database['summarycpcpk']

collection_mapping = {
    '!01': database['M01'],
    '!02': database['M02'],
    '!03': database['M03'],
    '!04': database['M04'],
    '!05': database['M05'],
    '!06': database['M06'],
    '!07': database['M07'],
    '!08': database['M08'],
    '!09': database['M09'],
    '!10': database['M10'],
    '!11': database['M11'],
}

collection_mapping2 = {
    'config_data_current': collection_2['current_usl_lsl'],
    'config_data_pulse': collection_2['pulse_usl_lsl'],
    'users': collection_2['users'],
    'machines':collection_2['machines'],
    'configuration_history':collection_2['configuration_history']
}

# Custom handler for invalid tokens
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": "Invalid token", "error": "invalid_token"}), 401

# Custom handler for missing tokens
@jwt.unauthorized_loader
def unauthorized_callback(error):
    return jsonify({"message": "Missing token", "error": "unauthorized"}), 401

# Custom handler for revoked tokens
@jwt.revoked_token_loader
def revoked_token_callback(error):
    return jsonify({"message": "Token has been revoked", "error": "revoked_token"}), 401

@app.route("/")
def dash_dashboard():
    return redirect("/dashapp/")

# Endpoint for obtaining a token
@app.route("/api/client_auth", methods=["POST"])
def get_token():
    client_key = request.json.get("client_key")
    client_secret = request.json.get("client_secret")

    if client_key in app.config["CLIENTS"] and app.config["CLIENTS"][client_key] == client_secret:
        access_token = create_access_token(identity=client_key)
        return jsonify({"access_token": access_token}), 200
    else:
        return jsonify({"message": "Invalid client credentials", "error": "invalid_credentials"}), 401

@app.route("/api/get_usl_lsl", methods=["GET"])
@jwt_required()
def get_data():
    configfile = client['configurationfiles']
    get_current_data = configfile['current_usl_lsl']
    get_pulse_data = configfile['pulse_usl_lsl']
    current_data = pd.DataFrame(list(get_current_data.find()))
    pulse_data = pd.DataFrame(list(get_pulse_data.find()))

    current_data['_id'] = current_data['_id'].astype(str)
    pulse_data['_id'] = pulse_data['_id'].astype(str)

    response_data = {
        'current_usl_lsl': current_data.to_dict(orient='records'),
        'pulse_usl_lsl': pulse_data.to_dict(orient='records')
    }
    return jsonify(response_data), 200


# Protected endpoint - requires a valid token
@app.route("/api/insertlog", methods=["POST", "GET"])
@jwt_required()
def protected():
    if request.method == "POST":
        with client.start_session() as session:
            data = request.get_json()
            if isinstance(data, list):
                for entry in data:
                    if 'machine_name' not in entry or 'current' not in entry or 'pulse' not in entry:
                        return jsonify(message="Missing data field"), 400
            else:
                if 'machine_name' not in data or 'current' not in data or 'pulse' not in data:
                    return jsonify(message="Missing data field"), 400
                data = [data]

            now = datetime.now()
            json_data = pd.DataFrame(data)
            json_data['created_time'] = now
            json_data['created_date'] = now.strftime('%Y/%m/%d')
            json_data['created_date'] = pd.to_datetime(json_data['created_date'])
            json_data['created_time'] = pd.to_datetime(json_data['created_time'])

            for entry in json_data.to_dict(orient='records'):
                if entry.get('strokes') is None:
                    continue
                if entry['current'] in ["0.00", "00.0"] or entry['pulse'] in ["0.00", "00.0"] or entry['strokes'] == '':
                    continue
                machine_name = entry['machine_name']
                for prefix, col in collection_mapping.items():
                    if machine_name.startswith(prefix):
                        existing_entry = col.find_one({'created_date': entry['created_date'], 'strokes': entry['strokes']})
                        if existing_entry:
                            continue
                        else:
                            col.insert_one(entry)

            return jsonify({"message": "Data inserted through API successfully"}), 200

    elif request.method == "GET":
        machine_name = request.args.get('machine_name')
        if machine_name is None:
            return jsonify({"message": "Missing 'machine_name' parameter in the request"}), 400
        collection = None
        for prefix, col in collection_mapping.items():
            if machine_name== prefix:
                collection = col
                break
        if collection is not None:
            last_records = collection.find().sort('_id', -1).limit(1).next()
            if last_records:
                last_records['_id'] = str(last_records['_id'])
                return jsonify({"last_record": last_records}), 200
            else:
                return jsonify({"message": "No records found for the specified machine_name"}), 404
        else:
            return jsonify({"message": f"Collection not found for machine_name: {machine_name}"}), 404

@app.route('/set_session', methods=['POST'])
def set_session():
    data = request.get_json()
    username = data.get('username')

    if username is not None:
        session['username'] = username
        return jsonify({'message': 'Session data set successfully'}), 200
    else:
        return jsonify({'message': 'Name not provided in the request'}), 400

@app.route('/get_session', methods=['GET'])
def get_session():
    username = session.get('username')

    if username:
        return jsonify({'username': username}), 200
    else:
        return jsonify({'message': 'No username found in session'}), 404


@app.errorhandler(400)
@app.errorhandler(401)
def handle_http_error(error):
    response = {
        'message': 'An error occurred',
        'status_code': error.code
    }
    return jsonify(response), error.code


@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"An unhandled exception occurred: {str(e)}")
    response = {
        "message": 'An unexpected error occurred',
        "status_code": 500
    }
    return jsonify(response), 500

