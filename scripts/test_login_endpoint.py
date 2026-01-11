import requests
import sys


def test_login():
    url = "http://127.0.0.1:8000/auth/login"
    payload = {
        "username": "franc",  # Assuming this user exists or we get 404/401, checking for connectivity
        "password": "wrongpassword",
    }

    print(f"Sending POST to {url}...")
    try:
        resp = requests.post(url, json=payload)
        print(f"Status Code: {resp.status_code}")
        print(f"Response: {resp.json()}")

        if resp.status_code in [200, 401, 404]:
            print("Server is responding correctly (Application Layer Reachable).")
        else:
            print("Server returned unexpected error.")

    except Exception as e:
        print(f"CONNECTION ERROR: {e}")
        print("The server might be down or blocking connections.")


if __name__ == "__main__":
    test_login()
