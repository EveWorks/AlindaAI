# Alinda Documentation

## Introduction

Alinda is a robust AI model designed to handle queries related to various academic and technical subjects. She can create charts, run code, do advanced data analytics, read/analyze stocks—basically, she's your own personal data scientist / expert maths professor. This documentation provides an overview of how to set up and use the Alinda API, including examples of how to make queries and handle responses.

## What She is Designed For

University Students & Professionals Learning Maths and Computer Science. She excells at that, and she can do much more as well. Below are some random tasks I assigned Alinda to do as a Data Scientist for CS Students and Some Example Maths Equations to Visualize.

## Some Visual Outputs :

![Maths Visual Learning](image-1.png)

![10 Popular Stocks Regression](images/all_stocks_linear_regression_normalized.png)

![Linear Regression](images/intc_linear_regression.png)

![XGBoost on CISCO Stock](image.png)


## Setup

### Dependencies

Ensure you have the following dependencies installed:

- `fastapi`
- `pydantic`
- `uvicorn`

You can install them using pip:

```bash
pip install fastapi pydantic uvicorn
```

To be completed added there are a lot.

### Importing Modules

Import the necessary modules and classes:

```python
from alinda_agent import LoadProfile
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os
import sys
import argparse
import uvicorn
from fastapi.responses import StreamingResponse
```

### FastAPI Configuration

Initialize the FastAPI application:

```python
app = FastAPI()
```

## Data Models

### QueryRequest

The `QueryRequest` class defines the structure of the request payload:

```python
class QueryRequest(BaseModel):
    query: str
    full_name: str
    major: str
    degree: str
    school: str
    year: str
    interests: List[str]
    wants_to_learn: List[str]
    previous_progress: dict
    messages: list
```

## Endpoints

### `/query/`

This endpoint handles standard queries to the Alinda AI model.

#### Request

- **Method**: POST
- **URL**: `/query/`
- **Headers**:
  - `Content-Type: application/json`
- **Body**:

```json
{
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
  "messages": [
    {
      "role": "assistant",
      "type": "message",
      "content": "The derivative of \\( x^2 \\) with respect to \\( x \\) can be calculated using the power rule..."
    }
  ]
}
```

#### Response

The response will be a JSON object containing the AI model's response to the query.

### `/streaming-query/`

This endpoint handles streaming queries to the Alinda AI model.

#### Request

- **Method**: POST
- **URL**: `/streaming-query/`
- **Headers**:
  - `Content-Type: application/json`
- **Body**:

```json
{
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
  "messages": [
    {
      "role": "assistant",
      "type": "message",
      "content": "The derivative of \\( x^2 \\) with respect to \\( x \\) can be calculated using the power rule..."
    }
  ]
}
```

#### Response

The response will be a streaming response containing the AI model's response to the query. The streaming response allows for real-time updates and continuous data flow, making it ideal for scenarios where immediate feedback is required.

## Example Usage

### Making a Query

```python
profile_information =  {
    'major': 'Computer Science',
    'degree': 'Bachelor',
    'school': 'Harvard University',
    'year': '2023',
    'interests': ['Machine Learning', 'Deep Learning', 'Computer Vision', 'Mathematics', 'Algorithms'],
    'wants_to_learn': ['Mathematics', 'Computer Science', 'Machine Learning', 'Deep Learning', 'Computer Vision', 'Algorithms'],
    'previous_progress': {
        'differential_equations': '50%',
        'linear_algebra': '75%',
        'calculus': '100%',
        'probability_theory': '25%',
        'statistics': '50%',
        'machine_learning': '25%',
        'tensorflow': '50%',
        'streamlit': '25%',
    }
}

messages = [{'role': 'assistant', 'type': 'message', 'content': "The derivative of \\( x^2 \\) with respect to \\( x \\) can be calculated using the power rule of differentiation. According to the power rule, if you have a function \\( f(x) = x^n \\), the derivative \\( f'(x) \\) is given by:\n\n\\[\nf'(x) = n \\cdot x^{n-1}\n\\]\n\nFor \\( f(x) = x^2 \\):\n\n1. Here, \\( n = 2 \\).\n2. Applying the power rule:\n\n\\[\nf'(x) = 2 \\cdot x^{2-1} = 2x\n\\]\n\nThus, the derivative of \\( x^2 \\) is \\( 2x \\).\n\nLet me know what you'd like to do next."}]

query_request = QueryRequest(
    query='What is the derivative of x^2?',
    full_name='Muneeb Ahmad',
    major=profile_information['major'],
    degree=profile_information['degree'],
    school=profile_information['school'],
    year=profile_information['year'],
    interests=profile_information['interests'],
    wants_to_learn=profile_information['wants_to_learn'],
    previous_progress=profile_information['previous_progress'],
    messages=messages
)

response = query(query_request)

second_query = QueryRequest(
    query='What is the derivative of x^3?',
    full_name='Muneeb Ahmad',
    major=profile_information['major'],
    degree=profile_information['degree'],
    school=profile_information['school'],
    year=profile_information['year'],
    interests=profile_information['interests'],
    wants_to_learn=profile_information['wants_to_learn'],
    previous_progress=profile_information['previous_progress'],
    messages=response
)

response_v2 = query(second_query)

print(response_v2)
```

## Queries for Backend Developers

### 1. Create a Chart for NVIDIA and Apple Stocks for the past 10 years

```json
{
  "query": "Create a chart for NVIDIA and Apple stocks for the past 10 years.",
  "full_name": "Backend Developer",
  "major": "Computer Science",
  "degree": "Bachelor",
  "school": "Harvard University",
  "year": "2023",
  "interests": ["Data Visualization", "Stock Analysis"],
  "wants_to_learn": ["Data Visualization", "Stock Analysis"],
  "previous_progress": {
    "data_visualization": "75%",
    "stock_analysis": "50%"
  },
  "messages": []
}
```

### 2. Find the Derivative of x**2 and Plot It

```json
{
  "query": "Find the derivative of x**2 and plot it.",
  "full_name": "Backend Developer",
  "major": "Computer Science",
  "degree": "Bachelor",
  "school": "Harvard University",
  "year": "2023",
  "interests": ["Calculus", "Data Visualization"],
  "wants_to_learn": ["Calculus", "Data Visualization"],
  "previous_progress": {
    "calculus": "100%",
    "data_visualization": "75%"
  },
  "messages": []
}
```

### 3. How to Find the Differential of an Equation Show Visually

```json
{
  "query": "How to find the differential of an equation show visually.",
  "full_name": "Backend Developer",
  "major": "Computer Science",
  "degree": "Bachelor",
  "school": "Harvard University",
  "year": "2023",
  "interests": ["Calculus", "Data Visualization"],
  "wants_to_learn": ["Calculus", "Data Visualization"],
  "previous_progress": {
    "calculus": "100%",
    "data_visualization": "75%"
  },
  "messages": []
}
```

### 4. Create a Quiz on Streamlit

```json
{
  "query": "Create a quiz on Streamlit.",
  "full_name": "Backend Developer",
  "major": "Computer Science",
  "degree": "Bachelor",
  "school": "Harvard University",
  "year": "2023",
  "interests": ["Web Development", "Streamlit"],
  "wants_to_learn": ["Web Development", "Streamlit"],
  "previous_progress": {
    "web_development": "50%",
    "streamlit": "25%"
  },
  "messages": []
}
```

## Running the Application

To run the FastAPI application, use the following command:

```bash
uvicorn main:app --reload
```

This will start the server on `http://localhost:6969`.

## Conclusion

This documentation provides a comprehensive guide to setting up and using the Alinda API. For further details, refer to the source code and additional documentation provided with the Alinda project.
