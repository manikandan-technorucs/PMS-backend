import urllib.request
import urllib.error
import json

payload = {
    "title": "Test Task",
    "project_id": None,
    "assignee_id": None,
    "task_list_id": None,
    "status_id": None,
    "priority_id": None,
    "start_date": None,
    "end_date": None,
    "estimated_hours": None,
    "description": None,
    "progress": 0
}

data = json.dumps(payload).encode('utf-8')

req = urllib.request.Request(
    "http://localhost:8000/api/v1/tasks/", 
    data=data, 
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer fake_token"
    },
    method='POST'
)

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8')
    print(f"HTTPError: {e.code}")
    print(f"Body: {body}")
except Exception as e:
    print(f"Exception: {e}")
