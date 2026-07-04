import sys
from fastapi.testclient import TestClient

import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

client = TestClient(app)

endpoints_to_test = [
    ("POST", "/api/v1/users/login", {"json": {"email": "test@test.com", "password": "password"}}),
    ("GET", "/api/v1/patients/1/dashboard", {}),
    ("GET", "/api/v1/doctors/1/patients", {}),
    ("GET", "/api/v1/doctors/1/receptionists", {}),
    ("GET", "/api/v1/medical-records/patient/1", {}),
    ("GET", "/api/v1/patient-diaries/", {}),
    ("GET", "/api/v1/patient-diaries/medical-record/1", {}),
    ("GET", "/api/v1/patient-diaries/1", {})
]

def run_tests():
    all_passed = True
    for method, url, kwargs in endpoints_to_test:
        print(f"Testing {method} {url}...")
        try:
            if method == "POST":
                response = client.post(url, **kwargs)
            elif method == "GET":
                response = client.get(url, **kwargs)
            else:
                continue
            
            if response.status_code == 500:
                print(f"FAIL: {method} {url} returned 500 Internal Server Error.")
                print(f"Response: {response.text}")
                all_passed = False
            else:
                print(f"PASS: {method} {url} returned {response.status_code}")
        except Exception as e:
            print(f"FAIL: {method} {url} raised an exception: {e}")
            all_passed = False

    if all_passed:
        print("\nAll endpoints passed without 500 Internal Server Error.")
        sys.exit(0)
    else:
        print("\nSome endpoints returned 500 Internal Server Error.")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
