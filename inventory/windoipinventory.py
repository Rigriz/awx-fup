#!/usr/bin/env python3

import requests
import json
import sys

# ==========================================
# API CONFIGURATION
# ==========================================

API_URL = "http://172.16.47.2:5000/api/labs/411B/computers"

# ==========================================
# WINRM CONFIGURATION
# ==========================================

WINRM_USER = "bmsit"
WINRM_PASSWORD = "123456"
WINRM_PORT = 5985

# ==========================================
# INITIALIZE AWX INVENTORY
# ==========================================

inventory = {
    "_meta": {
        "hostvars": {}
    },
    "all": {
        "hosts": []
    }
}

# ==========================================
# AWX DYNAMIC INVENTORY ARGUMENT
# ==========================================

if len(sys.argv) < 2 or sys.argv[1] != "--list":
    print(json.dumps({}))
    sys.exit(0)

# ==========================================
# FETCH COMPUTERS FROM API
# ==========================================

try:

    response = requests.get(
        API_URL,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    computers = data.get("data", [])

except requests.RequestException as error:

    print(
        json.dumps({
            "error": str(error),
            "_meta": {
                "hostvars": {}
            },
            "all": {
                "hosts": []
            }
        })
    )

    sys.exit(1)

except (ValueError, AttributeError) as error:

    print(json.dumps({
        "error": str(error),
        "_meta": {
            "hostvars": {}
        },
        "all": {
            "hosts": []
        }
    }))

    sys.exit(1)

# ==========================================
# PROCESS COMPUTERS
# ==========================================

for computer in computers:

    hostname = computer.get("hostname")
    ip = computer.get("ip")

    # Skip invalid records
    if not hostname or not ip:
        continue

    # Add W prefix to hostname
    # L21 -> WL21
    # R21 -> WR21

    hostname = hostname.strip().upper()
    ip = ip.strip()

    device_name = "W" + hostname

    # Add host to AWX inventory
    if device_name not in inventory["all"]["hosts"]:

        inventory["all"]["hosts"].append(device_name)

    # Assign host variables
    inventory["_meta"]["hostvars"][device_name] = {

        "ansible_host": ip,

        "ansible_connection": "winrm",

        "ansible_user": WINRM_USER,

        "ansible_password": WINRM_PASSWORD,

        "ansible_become_password": WINRM_PASSWORD,

        "ansible_port": WINRM_PORT,

        "ansible_winrm_transport": "ntlm",

        "ansible_winrm_server_cert_validation": "ignore"

    }

# ==========================================
# OUTPUT INVENTORY FOR AWX
# ==========================================

print(json.dumps(inventory, indent=4))
