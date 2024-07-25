import numpy as np
from scipy import stats
import pandas as pd
from datetime import datetime as datetime
import pymongo
from pymongo import MongoClient
import time
import flask
import logging
import csv
from app.routes import client, database, collection_mapping, collection_mapping2,summary_collection

collection_mapping = collection_mapping

login_details = client.login_events
log = login_details.login_events

def log_event(username, event_type):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file_path = 'logs/UserLogDetails.csv'

    try:
        with open(file_path, mode='a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            if csv_file.tell() == 0:
                writer.writerow(['timestamp', 'username', 'event_type'])
            writer.writerow([timestamp, username, event_type])
    except Exception as e:
        print(f"An error occurred while logging event: {e}")

def log_login_event(username):
    log_event(username, 'LOGGED IN')

def log_logout_event(username):
    log_event(username, 'LOGGED OUT')

def get_current_username():
    if flask.session.get('logged_in')  :
        username = flask.session['username']
        return username
    else:
        return None

class Dashboards:
    def __init__(self, machine_id, collection_mapping):
        self.machine_id = machine_id
        self.collection_mapping = collection_mapping
        self.df = pd.DataFrame()
        self.last_records_df = pd.DataFrame()

    def machine(self):
        all_records = []
        all_last_records = []

        if self.machine_id not in self.collection_mapping:
            raise ValueError(f"No collection found for machine ID: {self.machine_id}")

        collection = self.collection_mapping[self.machine_id]

        if collection is None:
            raise ValueError(f"No collection found for machine ID: {self.machine_id}")

        # Fetch the latest record for the collection
        try:
            last_record = collection.find({'machine_name': {'$regex': f'^{self.machine_id}'} }).sort('_id', -1).limit(1).next()
        except StopIteration:
            last_record = None  # Handle the case when no records are found

        if last_record:
            # Append the latest record to the list of all last records
            all_last_records.append(last_record)

            # Extract the date part from the created_date field
            last_record_date = last_record['created_date'].date()

            # Filter records for the same day as the latest record's created_date
            day_records = collection.find({
                'machine_name': {'$regex': f'^{self.machine_id}'},
                'created_date': {
                    '$gte': datetime.combine(last_record_date, datetime.min.time()),
                    '$lt': datetime.combine(last_record_date, datetime.max.time())
                }
            })

            # Extend the list of all records with the day_records
            all_records.extend(list(day_records))

        # Combine all records into one DataFrame
        self.df = pd.DataFrame(all_records)

        # Combine all last records into one DataFrame
        self.last_records_df = pd.DataFrame(all_last_records)

        return self.df, self.last_records_df


####All collections data #####
class DashboardMachines:
    def __init__(self, collection_mapping):
        self.collection_mapping = collection_mapping
        self.df = pd.DataFrame()

    def filter_and_get_last_non_zero_values(self):
        # Initialize an empty list to store DataFrames for each machine
        dfs = []

        # Step 1: Iterate through each collection
        for machine_identifier, collection in self.collection_mapping.items():
            if collection is None:
                raise ValueError(f"No collection found for machine identifier: {machine_identifier}")

            # Filter all machines that start with the specified identifier
            machines = collection.distinct('machine_name', {'machine_name': {'$regex': f'^{machine_identifier}'}})

            # Step 2: Iterate through each machine in the collection
            for machine in machines:
                # Filter records for the current machine
                machine_records = collection.find({'machine_name': machine})
                # Create a DataFrame for the current machine
                df = pd.DataFrame(machine_records)
                dfs.append(df)

        # Concatenate DataFrames for all machines in all collections
        self.df = pd.concat(dfs, ignore_index=True)

        # Check if the 'created_time' and 'value' columns exist in the DataFrame
        if 'created_time' not in self.df.columns or 'current_cp' not in self.df.columns:
            raise ValueError("DataFrame does not contain the required columns")

        # Step 3: Find the latest non-zero value for each machine
        latest_non_empty_records = self.df[self.df['current_cp'].notna() & (self.df['current_cp'] != '')].groupby('machine_name').apply(lambda x: x.iloc[-1])

        # Create a DataFrame for distinct last non-zero records
        distinct_last_non_zero_records_df = pd.DataFrame(latest_non_empty_records)

        return distinct_last_non_zero_records_df


def update_usl_lsl(df, collection_mapping2):
    configdatacurrent = pd.DataFrame(list(collection_mapping2['config_data_current'].find()))
    df2 = pd.merge(df, configdatacurrent, on='machine_name', how='left')
    df_row = df2.iloc[-1:]
    current_usl = df_row['usl'].values[0]
    current_lsl = df_row['lsl'].values[0]
    current_mean = df_row['mean'].values[0]
    current_rating_detail = df_row['rating(AMP)'].values[0]
    current_operation = df_row['operation'].values[0]

    configdatapulse = pd.DataFrame(list(collection_mapping2['config_data_pulse'].find()))
    df2 = pd.merge(df, configdatapulse, on='machine_name', how='left')
    df1_row = df2.iloc[-1]
    pulse_usl = df1_row['usl']
    pulse_lsl = df1_row['lsl']
    pulse_mean = df_row['mean'].values[0]
    pulse_rating_detail = df_row['rating(AMP)'].values[0]
    pulse_operation = df_row['operation'].values[0]

    return (current_usl, current_lsl,current_mean,current_rating_detail,current_operation,
            pulse_usl, pulse_lsl,pulse_mean,pulse_rating_detail,pulse_operation)


def pick_ratings(collection_mapping):
    all_machine_names = []
    for machine_identifier, collection in collection_mapping.items():
        all_machine_names.extend(collection.distinct('machine_name'))

    ratings = {}

    for machine_name in all_machine_names:
        machine_prefix = machine_name[:3]

        matching_machines = [m for m in all_machine_names if m.startswith(machine_prefix)]

        if len(matching_machines) > 1:
            matching_ratings = []
            for matching_machine in matching_machines:
                query = {'machine_name': matching_machine}
                cursor = collection_mapping[machine_identifier].find(query).sort('_id', -1).limit(1)

                try:
                    current_rating = next(cursor)
                    matching_ratings.append((matching_machine, current_rating))
                except StopIteration:
                    # Handle empty cursor gracefully
                    pass

            matching_ratings.sort(key=lambda x: x[1]['_id'], reverse=True)
            if matching_ratings:
                most_recent_machine, most_recent_rating = matching_ratings[0]
                ratings[most_recent_machine] = most_recent_rating
        else:
            query = {'machine_name': machine_prefix}
            cursor = collection_mapping[machine_prefix].find(query).sort('_id', -1).limit(1)

            try:
                current_rating = next(cursor)
                ratings[machine_name] = current_rating
            except StopIteration:
                # Handle empty cursor gracefully
                pass

    return ratings

def pick_machines(collection_mapping):
    last_machines = []

    for machine_identifier, collection in collection_mapping.items():
        if collection is not None:
            last_record = collection.find_one(sort=[('_id', -1)])
            if last_record:
                last_machine_name = last_record.get('machine_name')
                last_machines.append(last_machine_name)

    return last_machines

def machine_names(collection_mapping2):
    machine_data = pd.DataFrame(list(collection_mapping2['machines'].find()))
    machine_data[['mac_name', 'ratings']] = machine_data['machine_name'].str.extract(r'(\x21\d{2})(\d{3})')
    unique_machines = machine_data['mac_name'].unique()
    return unique_machines

def ratings(collection_mapping2, machine_name):
    # machine_data = pd.DataFrame(list(collection_mapping2['machines'].find()))
    machine_data = pd.DataFrame(list(collection_mapping2['machines'].find({"status": {"$ne": "INACTIVE"}})))
    machine_data[['mac_name', 'ratings']] = machine_data['machine_name'].str.extract(r'(\x21\d{2})(\d{3})')
    filtered_df = machine_data[machine_data['machine_name'].str.startswith(machine_name)].copy()
    filtered_df['ratings_schedule'] = filtered_df['ratings'] + " (" + filtered_df['rating(AMP)'].astype(str) + ")"
    options = [{'label': ratings, 'value': ratings} for ratings in filtered_df['ratings_schedule']]
    return options

def operation_name(collection_mapping2, machine_name):
    machine_data = pd.DataFrame(list(collection_mapping2['config_data_current'].find()))
    machine_data[['mac_name', 'ratings']] = machine_data['machine_name'].str.extract(r'(\x21\d{2})(\d{3})')
    filtered_df = machine_data[machine_data['machine_name'].str.startswith(machine_name)].copy()
    filtered_df['ratings_schedule'] = filtered_df['ratings'] + " (" + filtered_df['rating(AMP)'].astype(str) + ")"
    return filtered_df


num_machines = pick_machines(collection_mapping)

def calculate_condition_cpk(value):
    cond1 = 'PROCESS IS CAPABLE,MAINTAIN THE PROCESS PARAMETER'
    cond2 = 'PROCESS IS MARGINALLY CAPABLE, NEED TO SHIFT AT THE CENTER'
    cond3 = 'PROCESS IS NOT CAPABLE'
    if value >= 1.33:
        condition = cond1,'#008000'
    elif 1 <= value < 1.33:
        condition = cond2,'#FF7518'
    else:
        condition = cond3,'#FF0000'
    return condition


def calculate_condition_cp(value):
    cond1 = 'PROCESS IS EXCELLENT TO PRODUCE ITEM IN GIVEN TOLERANCE'
    cond2 = 'PROCESS IS GOOD TO PRODUCE ITEM IN GIVEN TOLERANCE'
    cond3 = "PROCESS IS MARGINAL TO PRODUCE ITEM  IN GIVEN TOLERANCE 'PROCESS VARIATION IS MORE' "
    if value >= 2:
        condition = cond1,'#008000'
    elif 1.33 <= value < 2:
        condition = cond2,'#FF7518'
    else:
        condition = cond3,'#FF0000'
    return condition

def upadte_summarycpcpk(summary_collection):
    data = pd.DataFrame(list(summary_collection.find()))
    return data
