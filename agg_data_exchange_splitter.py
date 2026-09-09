import time
import logging
import pandas as pd
import csv
from requests.exceptions import RequestException

from dhis2_env import get_api

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DHIS2 server credentials, read from .env (see .env.example)
api = get_api("NG_NCD_ROBOT")

# JSON file path
json_file_path = "Workaround-ADEX.json"

# SQL View ID to retrieve facilities
sql_view_id = "sbIwdtFTOOh"

exchange_uid = "tQ3bUoFoXXX"

# List of Program Indicator UIDs
program_indicators = [
    "JycuigrwOA0", "w1OIAqhocAx", "lsUw32leiJX",
    "EWpkCPCuJf3", "bLiMzdg6ZHz", "ApG3MF1VmOL",
    "kqKZiGQ5DW6", "HEhrrdabdGQ", "AoqqjFOJGmS"
]

program_indicators = [
    "JycuigrwOA0", "w1OIAqhocAx", "lsUw32leiJX",
    "EWpkCPCuJf3", "bLiMzdg6ZHz", "ApG3MF1VmOL",
    "kqKZiGQ5DW6", "HEhrrdabdGQ", "AoqqjFOJGmS"
]

# Function to load and update the JSON template with placeholders
def load_and_update_json(uid, period, facility_uid):
    with open(json_file_path, 'r') as f:
        json_data = json.load(f)

    # Replace placeholders
    json_str = json.dumps(json_data)
    json_str = json_str.replace('ddddddddddd', uid)  # Replace PI UID
    json_str = json_str.replace('ppppppppppp', period)  # Replace period
    json_str = json_str.replace('ooooooooooo', facility_uid)  # Replace facility UID

    return json.loads(json_str)

# Function to get facilities as a DataFrame
def get_facilities():
    try:
        response = api.get(f'sqlViews/{sql_view_id}/data')
        response.raise_for_status()
        data = response.json()

        # Extract rows from the response
        rows = data['listGrid']['rows']

        # Create a DataFrame with 'facility_uid' and 'facility_name' columns
        facilities = pd.DataFrame(rows, columns=['facility_uid', 'facility_name'])

        return facilities
    except RequestException as e:
        logger.error(f"Error retrieving facilities: {str(e)}")
        raise

# Store results for reporting
results = []

# Retrieve facilities data
facilities = get_facilities()

# Start processing each Program Indicator
for uid in program_indicators:
    logger.info(f"Processing Program Indicator: {uid}")
    pi_start_time = time.time()

    # Loop through each facility
    for _, row in facilities.iterrows():
        facility_uid = row['facility_uid']
        facility_name = row['facility_name']
        logger.info(f"Processing Facility: {facility_uid} - {facility_name}")

        # Update JSON with placeholders replaced
        updated_json = load_and_update_json(uid, "THIS_MONTH", facility_uid)

        # Track start time for performance measurement
        start_time = time.time()

        try:
            # POST updated JSON to the metadata endpoint
            response = api.post('metadata', json=updated_json, params={'mergeMode': 'REPLACE'})
            response.raise_for_status()

            # Run the aggregate data exchange
            exchange_response = api.post(f'aggregateDataExchanges/{exchange_uid}/exchange')
            exchange_response.raise_for_status()

            elapsed_time = time.time() - start_time
            logger.info(f"Success for Facility: {facility_uid} - Elapsed Time: {elapsed_time:.2f} seconds")

            results.append({
                'PI_uid': uid,
                'facility_uid': facility_uid,
                'facility_name': facility_name,
                'result': 'SUCCESS',
                'elapsed_time': f"{elapsed_time:.2f} seconds"
            })

        except RequestException as e:
            elapsed_time = time.time() - start_time
            logger.error(f"Error for Facility {facility_uid}: {str(e)}")

            results.append({
                'PI_uid': uid,
                'facility_uid': facility_uid,
                'facility_name': facility_name,
                'result': 'FAILED',
                'elapsed_time': f"{elapsed_time:.2f} seconds",
                'error': str(e)
            })

    pi_elapsed_time = time.time() - pi_start_time
    logger.info(f"Completed Program Indicator {uid} - Total Elapsed Time: {pi_elapsed_time:.2f} seconds")

# Write results to CSV
csv_file = "execution_results.csv"
with open(csv_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=[
        'PI_uid', 'facility_uid', 'facility_name', 'result', 'elapsed_time', 'error'
    ])
    writer.writeheader()
    writer.writerows(results)

logger.info(f"Execution report saved to {csv_file}")

# Print summary
for result in results:
    print(f"{result['PI_uid']} - {result['facility_uid']} - {result['facility_name']} - "
          f"{result['result']} - {result['elapsed_time']} - {result.get('error', '')}")
