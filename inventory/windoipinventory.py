#!/usr/bin/env python3

import requests
import json
import sys

# API URL
API_URL = "http://10.42.0.1:5000/api/labs/411B/computers"

# Initialize empty AWX inventory
inventory = {
    "_meta": {
        "hostvars": {}
    },
    "all": {
        "hosts": []
    }
}

try:
    # Fetch Windows computer details from API
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()

    data = response.json()

except Exception:
    # Return empty inventory if API fails
    print(json.dumps(inventory))
    sys.exit(0)


# Get computer list from API
computers = data.get("data", [])
print("list",computers)
# Iterate through all computers
for computer in computers:

    hostname = computer.get("hostname")
    ip = computer.get("ip")

    # Skip invalid entries
    if not hostname or not ip:
        continue

    # Add hostname to AWX inventory
    inventory["all"]["hosts"].append(hostname)

    # Generate password by adding 'w' to hostname
    password = "w" + hostname

    # Assign/update host variables
    inventory["_meta"]["hostvars"][hostname] = {
        "ansible_host": ip,
        "ansible_connection": "winrm",
        "ansible_user": "bmsit",
        "ansible_password": "123456",
        "ansible_become_password":"123456",
        "ansible_port": 5985,
        "ansible_winrm_transport": "ntlm",
        "ansible_winrm_server_cert_validation": "ignore"
    }


# Print final JSON inventory for AWX
print(json.dumps(inventory))
