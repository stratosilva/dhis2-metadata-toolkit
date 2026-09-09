"""
Shared helpers for reading DHIS2 connection details from the environment.

Credentials live in a local .env file (git-ignored); see .env.example for the
full list of variables. Each DHIS2 instance/account pair gets a prefix, and
three variables are derived from it:

    <PREFIX>_URL
    <PREFIX>_USERNAME
    <PREFIX>_PASSWORD

For example, prefix "NG_NCD_ROBOT" reads NG_NCD_ROBOT_URL, NG_NCD_ROBOT_USERNAME
and NG_NCD_ROBOT_PASSWORD.
"""

import os

from dhis2 import Api
from dotenv import load_dotenv

# Read the local .env file, if present. Real values live there, never in source.
load_dotenv()


def get_credentials(prefix):
    """
    Reads the URL, username and password for one DHIS2 instance from the environment.

    Args:
        prefix (str): The environment variable prefix, e.g. 'NG_NCD_ROBOT'.

    Returns:
        tuple: (url, username, password)

    Raises:
        RuntimeError: If any of the three variables is missing or empty.
    """
    keys = {suffix: f"{prefix}_{suffix}" for suffix in ("URL", "USERNAME", "PASSWORD")}
    values = {suffix: os.getenv(key) for suffix, key in keys.items()}

    missing = [keys[suffix] for suffix, value in values.items() if not value]
    if missing:
        raise RuntimeError(
            f"Missing environment variable(s): {', '.join(missing)}. "
            f"Copy .env.example to .env and fill in the values."
        )

    return values["URL"], values["USERNAME"], values["PASSWORD"]


def get_api(prefix):
    """
    Builds a dhis2.Api instance from environment variables.

    Args:
        prefix (str): The environment variable prefix, e.g. 'NG_NCD_ROBOT'.

    Returns:
        Api: A configured DHIS2 API client.
    """
    url, username, password = get_credentials(prefix)
    return Api(url, username, password)


def get_required(name):
    """
    Reads a single required environment variable.

    Args:
        name (str): The variable name, e.g. 'SMS_API_TOKEN'.

    Returns:
        str: The value.

    Raises:
        RuntimeError: If the variable is missing or empty.
    """
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing environment variable: {name}. "
            f"Copy .env.example to .env and fill in the values."
        )
    return value
