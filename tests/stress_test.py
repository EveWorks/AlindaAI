import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# API details
url = "http://localhost:6969/query/"
headers = {"Content-Type": "application/json"}
data = {
    "query": "Write a Python script to send a query to the AlindaAI API.",
    "full_name": "Muneeb Ahmad",
    "major": "computer science",
    "degree": "Computer Science",
    "school": "VNSGU",
    "year": "2024",
    "interests": ["data structure"],
    "wants_to_learn": [],
    "previous_progress": {},
    "messages": [
        {"role": "user", "type": "message", "content": "hello"},
        {"role": "assistant", "type": "message", "content": "Hello, Mitul! How can I assist you today? If you have any questions or need help with something specific, feel free to let me know!\n\nLet me know what you'd like to do next."},
        {"role": "user", "type": "message", "content": "hello"},
        {"role": "assistant", "type": "message", "content": "Hello again, Mitul! If there's anything specific you'd like to discuss or any assistance you need, just let me know. I'm here to help!\n\nLet me know what you'd like to do next."},
        {"role": "assistant", "type": "message-summary", "content": "Hello Mitul! I'm here to assist you with anything you need. Just let me know what you'd like to discuss next!"},
        {"role": "assistant", "content": "Hello Bilal! I'm here to assist you. How can I help you today?", "type": "message-summary"},
    ],
}

def send_request():
    """Sends a single request to the API and measures its latency."""
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=data)
        latency = time.time() - start_time
        return response.status_code, latency
    except requests.exceptions.RequestException as e:
        return None, None

def stress_test(max_requests_per_second, duration_seconds):
    """Stress tests the API with increasing requests per second.

    Args:
        max_requests_per_second (int): Maximum requests per second to test.
        duration_seconds (int): Duration for each test increment in seconds.
    """
    print("Starting stress test...")
    results = []

    for rps in range(1, max_requests_per_second + 1):
        print(f"Testing {rps} requests per second...")
        latencies = []
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=rps) as executor:
            futures = [executor.submit(send_request) for _ in range(rps * duration_seconds)]

            for future in as_completed(futures):
                status_code, latency = future.result()
                if latency is not None:
                    latencies.append(latency)

        end_time = time.time()
        avg_latency = sum(latencies) / len(latencies) if latencies else float('inf')
        results.append((rps, avg_latency, len(latencies), end_time - start_time))
        print(f"RPS: {rps}, Average Latency: {avg_latency:.2f}s, Successful Requests: {len(latencies)}")

    print("\nTest complete. Results:")
    for rps, avg_latency, successful, test_duration in results:
        print(f"{rps} RPS: Avg Latency: {avg_latency:.2f}s, Success: {successful}, Test Duration: {test_duration:.2f}s")

if __name__ == "__main__":
    # Parameters for the stress test
    MAX_REQUESTS_PER_SECOND = 50
    DURATION_SECONDS = 5

    stress_test(MAX_REQUESTS_PER_SECOND, DURATION_SECONDS)
