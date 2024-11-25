from alinda_agent import LoadProfile
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os
import sys
import argparse
import uvicorn
from fastapi.responses import StreamingResponse

# FastAPI Configuration

app = FastAPI()

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


@app.post("/query/")
def query(query_request: QueryRequest, summary="Query Alinda AI Model for a Standard Response. Provide Previous Messages to Load Session into Memory."):
    """
    Example CURL Request:
```  
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
  "messages": [
    {
      "role": "assistant",
      "type": "message",
      "content": "The derivative of \\( x^2 \\) with respect to \\( x \\) can be calculated using the power rule..."
    }
  ]
}'
```
    """
    profile = LoadProfile(query_request.full_name, preferences=query_request.model_dump())
    profile.load_llm_configurations()
    return profile.fastapi_response(query_request.query, query_request.model_dump(), messages=query_request.messages)

@app.post('/streaming-query/')
def streaming_query(query_request: QueryRequest, summary="Query Alinda AI Model for a Streaming Response. Provide Previous Messages to Load Session into Memory."):
    """
    Example CURL Request:
```    
    curl -X POST "http://localhost:6969/streaming-query/" \
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
  "messages": [
    {
      "role": "assistant",
      "type": "message",
      "content": "The derivative of \\( x^2 \\) with respect to \\( x \\) can be calculated using the power rule..."
    }
  ]
}'
```
    """
    profile = LoadProfile(query_request.full_name, preferences=query_request.model_dump())
    profile.load_llm_configurations()
    return StreamingResponse(profile.streaming_response(query_request.query, query_request.model_dump(), messages=query_request.messages), media_type='text/event-stream')



    
    """
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
    
    """
    
    