#!/usr/bin/env python3
import requests
import json
import sys

API_URL = "http://localhost:8090/inventroy"

# You can pass lab name as argument OR hardcode
LAB_NAME = "411C"

response = requests.get(API_URL)
data = response.json()

lab_data = data.get(LAB_NAME, {})

inventory = {
    "all": {"hosts": []},
    "_meta": {"hostvars": {}}
}

for side in lab_data:   # L, R
    inventory[side] = {"hosts": []}

    for device_name, details in lab_data[side].items():
        ip = details["ip"]

        inventory["all"]["hosts"].append(device_name)
        inventory[side]["hosts"].append(device_name)

        inventory["_meta"]["hostvars"][device_name] = {
             "ansible_host": ip,
             "ansible_user": "bmsit",
             "ansible_password": "123456",
             "ansible_ssh_common_args": "-o StrictHostKeyChecking=no"
         }

print(json.dumps(inventory))
