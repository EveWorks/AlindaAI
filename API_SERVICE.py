from alinda_agent import LoadProfile, BuildPersonalizedProfile
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Optional, Dict
from alinda_agent import SummarizeAgent
import os
import sys
import argparse
import uvicorn
from fastapi.responses import StreamingResponse
import logging

logging.basicConfig(level=logging.DEBUG)


# FastAPI Configuration

app = FastAPI()


class QueryRequest(BaseModel):
    query: str
    full_name: str
    major: str
    degree: Optional[str] = ""  # Made optional, default is None
    school: Optional[str] = ""  # Made optional, default is None
    year: str
    interests: Optional[List[str]] = []  # Made optional, default is an empty list
    wants_to_learn: List[str]
    previous_progress: Dict
    messages: list

class MessageObject(BaseModel):
  message: str
  role: str


@app.middleware("http")
async def log_request(request: Request, call_next):
    body = await request.body()  # Get the raw request body
    logging.debug(f"Request Body: {body.decode()}")
    response = await call_next(request)
    return response


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



    
@app.post('/personalize-using-session/')
def personalize_using_session(query_request: QueryRequest, summary="Personalize Alinda AI Model using Session Data."):

  personlize_agent = BuildPersonalizedProfile(query_request.model_dump(), messages=query_request.messages)
  return personlize_agent.build_profile()  


@app.post("/summarize-response")
def summarize_response(message_object: MessageObject, summary="Summarize the Response from Alinda AI Model for Speech Tasks."):
  
  """
  Example CURL Request:
  ```  
    curl -X POST "http://localhost:6969/summarize-response" \
      -H "Content-Type: application/json" \
      -d '{
        "message": "The derivative of x^2 with respect to x can be calculated using the power rule...",
        "role": "assistant"
      }'
  ```
  """
  
  message_content = message_object.message
  role = message_object.role
  
  try:
    response =  SummarizeAgent(message_content, role).summarize_openai()
  except Exception as e:
    response = {"error": str(e)}
  
  return response
  
  
    