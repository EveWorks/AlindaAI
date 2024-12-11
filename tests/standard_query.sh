curl -X POST "http://localhost:6969/query/" \
-H "Content-Type: application/json" \
-d '{
  "query": "What is the derivative of x^2?",
  "full_name": "Muneeb Ahmad",
  "major": "Computer Science",
  "degree": "Bachelor",
  "school": "Harvard University",
  "year": "2023",
  "interests": ["Machine Learning", "Deep Learning", "Computer Vision", "Mathematics", "Algorithms"],
  "wants_to_learn": ["Mathematics", "Computer Science", "Machine Learning", "Deep Learning", "Computer Vision", "Algorithms"],
  "previous_progress": {
    "differential_equations": "50%",
    "linear_algebra": "75%",
    "calculus": "100%",
    "probability_theory": "25%",
    "statistics": "50%",
    "machine_learning": "25%",
    "tensorflow": "50%",
    "streamlit": "25%"
  },
  {
    "query": "hello",
    "full_name": "Mitul Sarvaiya",
    "major": "computer science",
    "degree": "Computer Science",
    "school": "VNSGU",
    "year": "2024",
    "interests": [
        "data structure"
    ],
    "wants_to_learn": [],
    "previous_progress": {},
    "messages": [
        {
            "role": "user",
            "type": "message",
            "content": "hello"
        },
        {
            "role": "assistant",
            "type": "message",
            "content": "Hello, Mitul! How can I assist you today? If you have any questions or need help with something specific, feel free to let me know!"
        }
    ]
}'
