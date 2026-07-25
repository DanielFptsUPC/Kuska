import sys

import requests

photo_path = sys.argv[1] if len(sys.argv) > 1 else "test.jpg"

with open(photo_path, "rb") as f:
    response = requests.post(
        "http://127.0.0.1:8000/incidents",
        files={"photos": (photo_path, f, "image/jpeg")},
        data={
            "description": "grieta en la pared, prueba",
            "lat": -12.05,
            "lon": -77.03,
            "client_id": "test-1",
            "created_at_client": "2026-07-25T10:00:00Z",
        },
    )

print(response.status_code)
print(response.text)
