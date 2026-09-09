import json
from dhis2 import Api

from dhis2_env import get_credentials

def reorder_ethopia_first(options, priority_name="Ethiopia"):
    # Find Ethiopia
    eth = next((o for o in options if o["name"] == priority_name), None)
    if not eth:
        raise ValueError(f"{priority_name} not found.")

    others = [o for o in options if o["name"] != priority_name]
    reordered = [eth] + others

    # Assign sortOrder starting from 1
    for i, opt in enumerate(reordered, start=1):
        opt["sortOrder"] = i

    return reordered

def main(api_url, user, password):
    option_set_file = "country_option_set.json"

    with open(option_set_file, "r") as f:
        data = json.load(f)

    # Reorder options
    data["options"] = reorder_ethopia_first(data["options"])

    # Update DHIS2 via API
    api = Api(api_url, user, password)
    option_set_uid = data["id"]

    response = api.put(f"optionSets/{option_set_uid}", json=data)

    if response.status_code == 200:
        print("✅ OptionSet updated successfully.")
    else:
        print(f"❌ Failed to update OptionSet: {response.status_code}")
        print(response.json())

if __name__ == "__main__":
    # Credentials come from .env (see .env.example)
    main(*get_credentials("LOCAL"))
