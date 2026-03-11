import urllib.request
import json

endpoints = [
    "http://localhost:8000/api/v1/masters/roles",
    "http://localhost:8000/api/v1/masters/user-statuses",
    "http://localhost:8000/api/v1/masters/departments",
    "http://localhost:8000/api/v1/masters/skills",
]

for url in endpoints:
    req = urllib.request.Request(url, headers={"Authorization": "Bearer fake_token"})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"{url} -> Count: {len(data)}")
            if len(data) > 0:
                print(f"Sample: {data[0]}")
    except Exception as e:
        print(f"{url} -> Exception: {e}")
