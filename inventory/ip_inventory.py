#!/usr/bin/env python3
import requests
import json
import sys

inventory = {"_meta": {"hostvars": {}}, "all": {"hosts": []}}

try:
    response = requests.get("http://172.16.47.2:8090/inventory", timeout=5)
    response.raise_for_status()
    data = response.json()
except Exception:
    print(json.dumps(inventory))
    sys.exit(0)

lab = data.get("411C", {})
print("DATA got: ", lab)   # ❌ Problem: AWX cannot parse stdout that is not JSON

for side in ["R", "L"]:
    for device_name, info in lab.get(side, {}).items():
        ip = info.get("ip")
        if ip:
            inventory["all"]["hosts"].append(device_name)
            inventory["_meta"]["hostvars"][device_name] = {
                "ansible_host": ip,
                "ansible_user": "bmsit",
                "ansible_password": "123456",
                "ansible_ssh_common_args": "-o StrictHostKeyChecking=no"
            }

print(json.dumps(inventory))
