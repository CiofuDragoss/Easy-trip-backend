import asyncio
import websockets
import json
import random
import time
import csv

# testat pe contul dragoscoff2@gmail.com
BASE_URL = "ws://localhost:8000/ws/recommend"
DUMMY_TOKEN = "Bearer aici se pune jwt-ul de access"
USER_COUNT = 20
TIMEOUT_SECONDS = 25
CSV_FILE = "results_test_experiences.csv"
SUMMARY_CSV_FILE = "results_test_experiences_summary.csv"
results = []


async def simulate_user(user_id):
    start_time = time.time()
    try:
        async with websockets.connect(
            BASE_URL, extra_headers={"Authorization": DUMMY_TOKEN}
        ) as websocket:
            payload = {
                "MainQuestions": {
                    "distance": 1.5,
                    "budget": 3,
                    "region": {
                        "latitude": 44.4268,
                        "longitude": 26.1025,
                        "latitude_delta": 0,
                        "longitude_delta": 0,
                    },
                    "category": "Experiente",
                },
                "SecondaryQuestions": {
                    "indoorOutdoor": random.choice(["ambele", "indoor", "outdoor"]),
                    "physical": random.random(),
                },
            }

            await websocket.send(json.dumps(payload))

            while True:
                try:
                    response = await asyncio.wait_for(
                        websocket.recv(), timeout=TIMEOUT_SECONDS
                    )
                except asyncio.TimeoutError:
                    duration = round(time.time() - start_time, 2)
                    results.append((user_id, duration, "Timeout"))
                    return

                data = json.loads(response)

                if data.get("type") == "ping":
                    continue

                if data.get("stage") == "final":
                    duration = round(time.time() - start_time, 2)

                    if any(data.get("data", {}).values()):
                        results.append((user_id, duration, "Success"))
                    else:
                        results.append((user_id, duration, "EmptyData"))

                    return

    except Exception as e:
        duration = round(time.time() - start_time, 2)
        results.append((user_id, duration, f"Error: {str(e)}"))


async def main():
    print(f"Simulam {USER_COUNT} utilizatori simultan...\n")
    tasks = [simulate_user(i) for i in range(1, USER_COUNT + 1)]
    await asyncio.gather(*tasks)

    with open(CSV_FILE, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["User ID", "Duration (s)", "Status"])
        writer.writerows(results)

    success_count = sum(1 for r in results if r[2] == "Success")
    timeout_count = sum(1 for r in results if r[2] == "Timeout")
    error_count = len(results) - success_count - timeout_count
    with open(SUMMARY_CSV_FILE, mode="w", newline="") as summary_file:
        writer = csv.writer(summary_file)
        writer.writerow(["Total Users", "Successes", "Timeouts", "Errors"])
        writer.writerow([USER_COUNT, success_count, timeout_count, error_count])


if __name__ == "__main__":
    asyncio.run(main())
