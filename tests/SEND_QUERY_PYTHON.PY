import requests

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
    "messages": [{"role":"user","type":"message","content":"hello"},{"role":"assistant","type":"message","content":"Hello, Mitul! How can I assist you today? If you have any questions or need help with something specific, feel free to let me know!\n\nLet me know what you'd like to do next."},{"role":"user","type":"message","content":"hello"},{"role":"assistant","type":"message","content":"Hello again, Mitul! If there's anything specific you'd like to discuss or any assistance you need, just let me know. I'm here to help!\n\nLet me know what you'd like to do next."},{"role":"assistant","type":"message-summary","content":"Hello Mitul! I'm here to assist you with anything you need. Just let me know what you'd like to discuss next!"},
                 {'role': 'assistant', 'content': "Hello Bilal! I'm here to assist you. How can I help you today?", 'type': 'message-summary'}],
}

response = requests.post(url, headers=headers, json=data)

# Print the response
print(f"Status Code: {response.status_code}")
print(f"Response Text: {response.text}")
