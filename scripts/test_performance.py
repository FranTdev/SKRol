import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"


def benchmark(name, url, method="GET", payload=None):
    times = []
    print(f"--- Benchmarking {name} ---")
    for i in range(5):
        start = time.time()
        try:
            if method == "GET":
                requests.get(url)
            elif method == "POST":
                requests.post(url, json=payload)
        except Exception as e:
            print(f"Error: {e}")
            return
        end = time.time()
        duration = (end - start) * 1000
        times.append(duration)
        print(f"Run {i + 1}: {duration:.2f}ms")

    avg = sum(times) / len(times)
    print(f"Average: {avg:.2f}ms\n")


def run_benchmarks():
    # 1. Root (Simple Ping)
    benchmark("Root /", f"{BASE_URL}/")

    # 2. Login (DB Read + Hash Check)
    # We need a valid user for a fair test, but even a 404 is a DB hit.
    benchmark(
        "Login Flow (DB Hit)",
        f"{BASE_URL}/auth/login",
        "POST",
        {"username": "benchmark_user", "password": "benchmark_password"},
    )

    # 3. User Search (DB Like Query)
    benchmark("User Search", f"{BASE_URL}/auth/users/search?username=test")


if __name__ == "__main__":
    run_benchmarks()
