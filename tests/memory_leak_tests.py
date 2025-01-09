import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# API details
url = "http://localhost:6969/query/"
headers = {"Content-Type": "application/json"}

# Base data structure
def create_request_data(full_name):
    """Creates the request payload with a unique name."""
    return {
        "query": "Say my name 10 times again and again!",
        "full_name": full_name,
        "major": "computer science",
        "degree": "Computer Science",
        "school": "VNSGU",
        "year": "2024",
        "interests": ["data structure"],
        "wants_to_learn": [],
        "previous_progress": {},
        "messages": [{"role": "user", "type": "message", "content": "Hello."}],
    }

# Function to send a request
def send_request(full_name):
    """Sends a single request to the API."""
    payload = create_request_data(full_name)
    print(f"Sending request for {full_name} with payload: {payload}")  # Debug statement
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Received response for {full_name}: {response.status_code}")  # Debug statement
        if response.status_code == 200:
            print(f"Response content for {full_name}: {response.text}")  # Debug statement
            return response.text  # Return the response as a string
        else:
            print(f"API returned status {response.status_code} for {full_name}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {full_name}: {e}")
        return None

# Function to check for name mixing in responses
def analyze_responses(response_text, own_name, other_name):
    """Checks if the response mentions the other name."""
    if not response_text:
        return False
    return other_name in response_text

# Concurrent test
def concurrent_test(num_requests):
    names = [("Miles", "Muneeb"), ("Muneeb", "Miles")]
    results = {name: [] for name, _ in names}

    # Generate request names based on the num_requests
    test_names = [("Miles", "Muneeb") if i % 2 == 0 else ("Muneeb", "Miles") for i in range(num_requests)]

    with ThreadPoolExecutor(max_workers=num_requests) as executor:
        futures = {
            executor.submit(send_request, own_name): (own_name, other_name)
            for own_name, other_name in test_names
        }
        for future in as_completed(futures):
            own_name, other_name = futures[future]
            try:
                response_text = future.result()
                results[own_name].append(response_text)
                print(f"Processed request for {own_name}.")  # Debug statement
            except Exception as e:
                print(f"Error processing request for {own_name}: {e}")

    # Analyze results
    for own_name, responses in results.items():
        other_name = "Muneeb" if own_name == "Miles" else "Miles"
        for response_text in responses:
            if response_text:
                if analyze_responses(response_text, own_name, other_name):
                    print(f"ERROR: Response for {own_name} mentions {other_name}!")
                else:
                    print(f"SUCCESS: Response for {own_name} does not mention {other_name}.")
            else:
                print(f"ERROR: No response received for {own_name}.")

if __name__ == "__main__":
    NUM_CONCURRENT_REQUESTS = 20  # Set this to 10 or 20 as needed
    concurrent_test(NUM_CONCURRENT_REQUESTS)