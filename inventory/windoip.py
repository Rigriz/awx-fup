#!/usr/bin/env python3
"""
AWX dynamic inventory for Lab 411B.

Configure this script as an AWX Sourced Inventory (custom script).
Set ANSIBLE_BMSIT_PASSWORD in the execution environment or inject it
through an AWX custom credential. Do not store the password in this file.
"""

import json
import os
import sys

import requests

API_URL = os.getenv(
    "LAB_INVENTORY_API_URL",
    "http://172.16.47.10:5000/api/labs/411B/computers",
)
LAB_GROUP = "lab_411B"
ANSIBLE_USER = os.getenv("ANSIBLE_BMSIT_USER", "BMSIT")
ANSIBLE_PASSWORD = os.getenv("ANSIBLE_BMSIT_PASSWORD")

def fail(message):
    print(f"Dynamic inventory error: {message}", file=sys.stderr)
    sys.exit(1)

def main():
    if not ANSIBLE_PASSWORD:
        fail(
            "ANSIBLE_BMSIT_PASSWORD is not set. "
            "Inject it through an AWX credential or environment variable."
        )

    try:
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        fail(f"Could not retrieve lab inventory from {API_URL}: {exc}")
    except ValueError:
        fail("The lab inventory API did not return valid JSON.")

    # Expected API response:
    # {
    #   "success": true,
    #   "lab": "411B",
    #   "total_computers": 59,
    #   "data": [{"hostname": "L21", "system_name": "L21",
    #             "ip": "...", "mac": "...", ...}]
    # }
    if payload.get("success") is not True:
        fail(f"API reported failure: {payload}")

    computers = payload.get("data")
    if not isinstance(computers, list):
        fail("API response is missing the expected 'data' list.")

    inventory = {
        "_meta": {"hostvars": {}},
        "all": {"children": [LAB_GROUP]},
        LAB_GROUP: {"hosts": []},
    }

    for computer in computers:
        if not isinstance(computer, dict):
            continue

        # Use system_name as the stable Ansible inventory hostname.
        host_name = computer.get("system_name") or computer.get("hostname")
        ip_address = computer.get("ip")
        mac_address = computer.get("mac")

        if not host_name or not ip_address:
            print(
                f"Skipping record without hostname/system_name or IP: {computer}",
                file=sys.stderr,
            )
            continue

        inventory[LAB_GROUP]["hosts"].append(host_name)
        inventory["_meta"]["hostvars"][host_name] = {
            "ansible_host": ip_address,
            "ansible_connection": "ssh",
            "ansible_user": ANSIBLE_USER,
            "ansible_password": ANSIBLE_PASSWORD,
            "ansible_become": True,
            "ansible_become_password": ANSIBLE_PASSWORD,
            "ansible_ssh_common_args": "-o StrictHostKeyChecking=no",
            "system_name": host_name,
            "mac_address": mac_address,
            "computer_status": computer.get("status"),
            "last_seen": computer.get("last_seen"),
            "lab_name": payload.get("lab", "411B"),
        }

    if not inventory[LAB_GROUP]["hosts"]:
        fail("API returned no usable computers; refusing to publish an empty inventory.")

    print(json.dumps(inventory))

if __name__ == "__main__":
    main()
