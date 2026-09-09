import os

import requests

from dhis2_env import get_api, get_required

# Define the variables. Credentials come from .env (see .env.example).
sms_api_token = get_required("SMS_API_TOKEN")

# List of phone numbers to notify in case of error, comma-separated in .env
phone_numbers = [
    number.strip()
    for number in os.getenv("ALERT_PHONE_NUMBERS", "").split(",")
    if number.strip()
]

# Connect to the DHIS2 API
api = get_api("NG_NCD_ROBOT")

# Query the job configuration status
try:
    job_result = api.get(
        'jobConfigurations/RuRpg4bbOWq',
        params={"fields": "*"}
    ).json()["lastExecutedStatus"]
except Exception as e:
    print(f"Failed to retrieve job status: {e}")
    job_result = None

# Define the function to send SMS
def send_sms(phone_number, message):
    """
    Sends an SMS using the SmartSMSSolutions API.
    """
    url = "https://app.smartsmssolutions.com/io/api/client/v1/sms/"
    payload = {
        "token": sms_api_token,
        "to": phone_number,
        "message": message,
        "sender": "FMOHNHCI",
        "type": "0",
        "routing": "3"
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("code") == 1000:
                print(f"SMS sent successfully to {phone_number}!")
            else:
                print(f"Failed to send SMS to {phone_number}. Response: {response_data}")
        else:
            print(f"Failed to send SMS to {phone_number}. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending SMS to {phone_number}: {e}")

# Check if the job status is 'STOPPED'
if job_result == "STOPPED":
    if not phone_numbers:
        print("ALERT_PHONE_NUMBERS is not set, so there is nobody to notify.")
    print("Job status is STOPPED. Sending SMS notifications...")
    message = "DHIS2 ERROR - AGG Data Exchange job failed to run last night. Please contact support."
    for phone in phone_numbers:
        print(phone + " " + message)
        #send_sms(phone, message)
else:
    print(f"Job status is {job_result}. No issues detected.")
