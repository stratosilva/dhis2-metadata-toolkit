import argparse
import os
import re
from datetime import datetime, timedelta
from dhis2 import Api
from dotenv import load_dotenv
import requests

# Read the local .env file, if present. Real values live there and never in this file.
load_dotenv()

sms_api_token = os.getenv("SMS_API_TOKEN")

# Added "default" English templates
message_template_tomorrow = {
    "kn":
        "Barka de, {patient_name} kije {facility_name} gobe domin ayi maki gwaji da Baki maganin chiwan hawan jini",
    "og":
        "{patient_name}, yoju si ile-iwosan {facility_name} ni ola fun ayewo funpa ati ogun re",
    "default":
        "Dear {patient_name}, please Visit {facility_name} tomorrow for a BP measure and medicines."
}

message_template_3_days_overdue = {
    "kn":
        "{patient_name}, muna jiranki yau a {facility_name} domin gwadaki da Kuma Baki magunguna",
    "og":
        "{patient_name}, an reti e loni jowo se abewo si ile-iwosan {facility_name} fun ayewo funpa ati ogun re",
    "default":
        "{patient_name} we are expecting you today, please visit {facility_name} for a BP measure and medicines."
}






def send_sms(phone_number, message):
    """
    Sends an SMS using the SmartSMSSolutions API.

    Args:
        phone_number (str): The recipient's phone number in the format '0[789]XXXXXXXXX'.
        message (str): The SMS message content.
    """
    if not sms_api_token:
        print(
            f"SMS_API_TOKEN is not set, so no SMS was sent to {phone_number}. "
            f"Copy .env.example to .env and fill in the token."
        )
        return

    # API endpoint for sending SMS via SmartSMSSolutions
    url = "https://app.smartsmssolutions.com/io/api/client/v1/sms/"

    # Payload with the necessary parameters
    payload = {
        "token": sms_api_token,        # API token for authentication
        "to": phone_number,            # Recipient's phone number
        "message": message,            # The SMS message content
        "sender": "FMOHNHCI",          # Optional: Sender ID
        "type": "0",                   # Optional: 0 for normal SMS, 1 for Flash SMS
        "routing": "3"                 # Optional: Route type (default is 3)
    }

    try:
        # Sending the POST request to the SMS gateway
        response = requests.post(url, data=payload)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
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


def extract_instances(response, collection_name):
    """
    Extracts the list of objects out of a tracker export response.

    Up to DHIS2 2.40 the tracker export endpoints wrapped their results in an 'instances' key.
    In 2.41 that key was deprecated in favour of a key named after the plural of the entity
    ('events', 'trackedEntities', ...) and both were returned. In 2.42 'instances' was removed,
    so reading only 'instances' silently yields an empty list on 2.42+.

    Args:
        response (dict): The parsed JSON body of a tracker export request.
        collection_name (str): The plural entity name, e.g. 'events' or 'trackedEntities'.

    Returns:
        list: The exported objects.
    """
    if collection_name in response:
        return response[collection_name]
    # Fall back to the pre-2.42 wrapper key
    return response.get('instances', [])


def get_targeted_events(api, program_uid, root_org_unit, program_stage_uid, target_date, status):
    """
    Retrieves targeted events from DHIS2 based on the specified criteria, manually filtering by status.

    Note:
    The 'OVERDUE' status filter may not work as expected when passed as a parameter in the API request.
    To handle this, the status parameter is omitted from the API call, and the filtering is done manually
    after retrieving the events.

    Args:
        api (Api): The DHIS2 API instance.
        program_uid (str): UID of the program.
        root_org_unit (str): UID of the root organisation unit.
        program_stage_uid (str): UID of the program stage.
        target_date (str): The target date in 'YYYY-MM-DD' format.
        status (str): The status of events to retrieve ('SCHEDULE' or 'OVERDUE').

    Returns:
        list: A list of event instances that match the specified status.
    """
    # Construct the filter parameters without the status filter.
    # 'ouMode' and 'skipPaging' were deprecated in 2.41 and removed in 2.42. The org unit
    # parameter stays singular on this endpoint: 'orgUnits' is silently ignored and the
    # request then fails with E1003 (no org unit for orgUnitMode DESCENDANTS).
    params = {
        "orgUnit": root_org_unit,
        "orgUnitMode": "DESCENDANTS",
        "program": program_uid,
        "programStage": program_stage_uid,
        "fields": "trackedEntity,orgUnit,scheduledAt,status",
        "scheduledAfter": target_date,
        "scheduledBefore": target_date,
        "paging": "false"
    }

    # Fetch events from the DHIS2 API
    events_response = api.get('tracker/events', params=params).json()

    # Retrieve the list of events
    events = extract_instances(events_response, 'events')
    print(f"Fetched {len(events)} events scheduled on {target_date} (before filtering on status {status}).")

    # Manually filter events by status
    filtered_events = [event for event in events if event.get('status') == status]

    # Return the filtered events
    return filtered_events


def get_tracked_entity_attributes(api, program_uid, tracked_entity_uid):
    """
    Retrieves attributes of a tracked entity.

    Args:
        api (Api): The DHIS2 API instance.
        program_uid (str): UID of the program.
        tracked_entity_uid (str): UID of the tracked entity.

    Returns:
        list: A list of attribute dictionaries.
    """
    # Fetch the tracked entity directly by UID. The collection endpoint requires an org unit
    # scope since 2.41, whereas the single-object endpoint does not.
    params = {
        "program": program_uid,
        "fields": "attributes"
    }

    response = api.get(f'tracker/trackedEntities/{tracked_entity_uid}', params=params).json()

    return response.get('attributes', [])


def get_org_unit_name(api, org_unit_uid, org_unit_cache):
    """
    Retrieves the name of an organisation unit, utilizing a cache to minimize API calls.

    Args:
        api (Api): The DHIS2 API instance.
        org_unit_uid (str): UID of the organisation unit.
        org_unit_cache (dict): Cache dictionary for organisation unit names.

    Returns:
        str: Name of the organisation unit.
    """
    # Check if the organisation unit name is already cached
    if org_unit_uid in org_unit_cache:
        return org_unit_cache[org_unit_uid]

    # Fetch the organisation unit name by its UID
    response = api.get(f'organisationUnits/{org_unit_uid}', params={"fields": "name"}).json()
    org_unit_name = response.get('name', 'Unknown Facility')

    # Cache the result
    org_unit_cache[org_unit_uid] = org_unit_name

    return org_unit_name


def normalize_phone_number(phone_number):
    r"""
    Normalizes and validates Nigerian phone numbers.

    Rules:
        - Remove country code prefixes (+234, 00234, 234).
        - Ensure the number starts with '07', '08', or '09'.
        - After processing, the number should match the regex '0[789]\d{9}'.

    Args:
        phone_number (str): The raw phone number.

    Returns:
        str: The normalized phone number in the format '0[789]XXXXXXXXX'.

    Raises:
        ValueError: If the phone number does not conform to the expected format.
    """
    original_phone_number = phone_number  # For error messages

    # Remove any whitespace or non-digit characters except '+'
    phone_number = phone_number.strip()

    # Remove country code prefixes
    if phone_number.startswith('+234'):
        phone_number = phone_number[4:]
    elif phone_number.startswith('00234'):
        phone_number = phone_number[5:]
    elif phone_number.startswith('234'):
        phone_number = phone_number[3:]

    # Remove any leading '+' after stripping country code
    phone_number = phone_number.lstrip('+')

    # Add leading '0' if missing and starts with '7', '8', or '9'
    if phone_number.startswith(('7', '8', '9')):
        phone_number = '0' + phone_number

    # Ensure the phone number matches the desired format
    if re.fullmatch(r'0[789]\d{9}', phone_number):
        return phone_number
    else:
        raise ValueError(f"Invalid Nigerian phone number format: {original_phone_number}")


def process_events(api, events, program_uid, org_unit_cache, message_templates):
    """
    Processes a list of events, sends SMS messages to valid phone numbers.

    Args:
        api (Api): The DHIS2 API instance.
        events (list): List of event instances.
        program_uid (str): UID of the program.
        org_unit_cache (dict): Cache dictionary for organisation unit names.
        message_templates (dict): Dict with message templates for Kano (kn) and Ogun (og)
        DEPRECATED: message_template (str): Template for the SMS message.
    """
    for event in events:
        tracked_entity_uid = event.get('trackedEntity')
        org_unit_uid = event.get('orgUnit')

        # Fetch the tracked entity attributes
        attributes = get_tracked_entity_attributes(api, program_uid, tracked_entity_uid)

        # Extract patient name and phone number
        patient_name = None
        phone_number = None

        for attribute in attributes:
            if attribute.get('attribute') == 'R6VkX5nsAy4':  # Patient name UID
                patient_name = attribute.get('value')
            elif attribute.get('attribute') == 'YRDy9xy9jD0':  # Phone number UID
                phone_number = attribute.get('value')

        if not patient_name or not phone_number:
            print(f"Patient with TEI {tracked_entity_uid} is missing required attributes. SMS cannot be sent.")
            continue

        try:
            normalized_phone = normalize_phone_number(phone_number)
        except ValueError as e:
            print(f"Error processing phone number for TEI {tracked_entity_uid}: {e}. SMS cannot be sent.")
            continue

        facility_name = get_org_unit_name(api, org_unit_uid, org_unit_cache)

        # --- MODIFIED TEMPLATE ROUTING & FALLBACK LOGIC ---
        state_acronym = facility_name[:2].lower()  # Normalize to lowercase just in case

        if state_acronym in ["kn", "og"]:
            msg_template = message_templates[state_acronym]
            # Strip state code prefix (e.g., "kn General Hospital" -> "General Hospital")
            display_facility_name = facility_name[3:]
        else:
            msg_template = message_templates["default"]
            # Keep full name since there is no state prefix to strip
            display_facility_name = facility_name

        message = msg_template.format(patient_name=patient_name, facility_name=facility_name[3:])
        print(f"Sending SMS to {normalized_phone}: {message}")
        #send_sms(normalized_phone, message)


def main():
    """
    Main function to execute the script logic.
    """
    # Argument parsing
    parser = argparse.ArgumentParser(description="DHIS2 API Integration for Sending SMS Notifications")
    parser.add_argument('--url', type=str, required=True, help='DHIS2 instance URL')
    parser.add_argument('--user', type=str, required=True, help='DHIS2 username')
    parser.add_argument('--password', type=str, required=True, help='DHIS2 password')

    args = parser.parse_args()

    # Initialize the API of the DHIS2 instance
    api = Api(args.url, args.user, args.password)

    # Check if the API is initialized correctly
    print(f"Running DHIS2 version {api.version} revision {api.revision}")

    # Set the necessary variables
    program_uid = "pMIglSEqPGS"
    root_org_unit = "uS2CuRbDyD7"
    program_stage_uid = "anb2cjLx3WM"

    # Create a cache for organisation unit names
    org_unit_cache = {}

    # Calculate dates for tomorrow and 3 days ago
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    three_days_ago_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')

    # Get the events scheduled for tomorrow with status 'SCHEDULE'
    scheduled_events = get_targeted_events(
        api, program_uid, root_org_unit, program_stage_uid, tomorrow_date, "SCHEDULE"
    )
    print(f"Found {len(scheduled_events)} scheduled events for tomorrow.")
    # Process and send SMS for scheduled events
    process_events(
        api,
        scheduled_events,
        program_uid,
        org_unit_cache,
        message_templates=message_template_tomorrow
        #message_template="Dear {patient_name}, please Visit {facility_name} tomorrow for a BP measure and medicines."
    )

    # Get the events that are overdue and scheduled from 3 days ago (some overdue will still have status SCHEDULE)
    overdue_events = get_targeted_events(
        api, program_uid, root_org_unit, program_stage_uid, three_days_ago_date, "OVERDUE"
    )
    print(f"Found {len(overdue_events)} overdue events from 3 days ago.")

    scheduled_3_days_ago_events = get_targeted_events(
        api, program_uid, root_org_unit, program_stage_uid, three_days_ago_date, "SCHEDULE"
    )
    print(f"Found {len(scheduled_3_days_ago_events)} scheduled events from 3 days ago.")

    # Merge overdue and scheduled events from 3 days ago
    events_from_3_days_ago = overdue_events + scheduled_3_days_ago_events
    print(f"Total events to process from 3 days ago: {len(events_from_3_days_ago)}")

    # Process and send SMS for overdue and scheduled events from 3 days ago
    process_events(
        api,
        events_from_3_days_ago,
        program_uid,
        org_unit_cache,
        message_templates=message_template_3_days_overdue
        #message_template="{patient_name}, we are expecting you today, please visit {facility_name} for a BP measure and medicines."
    )


if __name__ == "__main__":
    main()
