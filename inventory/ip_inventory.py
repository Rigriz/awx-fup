#!/usr/bin/env python3
import requests
import json
import sys
# Initialize empty inventory
inventory = {"_meta": {"hostvars": {}}, "all": {"hosts": []}}
try:
    # Fetch inventory from your API
    response = requests.get("http://172.16.47.2:8090/inventory", timeout=5)
    response.raise_for_status()  # Raise error for HTTP issues
    data = response.json()
except Exception:
    # If API fails, return empty inventory
    print(json.dumps(inventory))
    sys.exit(0)
# Select the lab you want
lab = data.get("411C", {})
# Iterate over sides (R/L) and devices
for side in ["R", "L"]:
    for device_name, info in lab.get(side, {}).items():
        ip = info.get("ip")
        if ip:
            # Add host to inventory
            inventory["all"]["hosts"].append(device_name)
            # Add host variables
            inventory["_meta"]["hostvars"][device_name] = {
                "ansible_host": ip,
                "ansible_user": "bmsit",
                "ansible_password": "123456",
                "ansible_ssh_common_args": "-o StrictHostKeyChecking=no"
            }
# Print JSON for AWX/Ansible
print(json.dumps(inventory))
