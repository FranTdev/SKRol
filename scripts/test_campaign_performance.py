import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"


def get_test_user():
    try:
        # Search for a user to get an ID
        resp = requests.post(f"{BASE_URL}/auth/users/search?username=a")
        if resp.status_code == 200 and resp.json():
            return resp.json()[0]["id"]
    except:
        return None
    return None


def benchmark_campaigns():
    print("Fetching test user...")
    # Since search is a GET in my code (auth.py says @router.get("/users/search"))
    # but requests.post was used in my thought? let's check auth.py
    # auth.py: @router.get("/users/search")

    try:
        resp = requests.get(f"{BASE_URL}/auth/users/search?username=a")
        if not resp.ok:
            print("Could not find users to test with.")
            return

        users = resp.json()
        if not users:
            print("No users found.")
            return

        user_id = users[0]["id"]
        print(f"Testing with User ID: {user_id}")

        times = []
        for i in range(5):
            start = time.time()
            r = requests.get(f"{BASE_URL}/campaigns/{user_id}")
            end = time.time()
            print(
                f"Fetch Campaigns Run {i + 1}: {(end - start) * 1000:.2f}ms. Status: {r.status_code}"
            )
            times.append((end - start) * 1000)

        print(f"Average: {sum(times) / len(times):.2f}ms")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    benchmark_campaigns()
