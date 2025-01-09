from alinda_agent import LoadProfile, BuildPersonalizedProfile
from fastapi import FastAPI, Request, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
from alinda_agent import SummarizeAgent
import os
import sys
import argparse
import uvicorn
from fastapi.responses import StreamingResponse
import logging
import subprocess
from fastapi import FastAPI, HTTPException
import multiprocessing
import time
from typing import Any
from fastapi import FastAPI, BackgroundTasks
from concurrent.futures import ThreadPoolExecutor
from typing import Any
import multiprocessing
from concurrent.futures import ProcessPoolExecutor


executor = ProcessPoolExecutor(max_workers=20)

#logging.basicConfig(level=logging.DEBUG)


# FastAPI Configuration

app = FastAPI()

import sentry_sdk

sentry_sdk.init(
    dsn="https://49e1d3ec4fd1add3d268dd3611b1a0d8@o4508454576652288.ingest.de.sentry.io/4508454592774224",
)

# add cors for alinda.muneeb.co
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


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

def process_query(query_request: QueryRequest, queue: multiprocessing.Queue):
    # Simulate the processing logic
    profile = LoadProfile(query_request.full_name, preferences=query_request.model_dump())
    profile.load_llm_configurations()
    answer = profile.fastapi_response(query_request.query, query_request.model_dump(), messages=query_request.messages)
    print('Putting Answer Back Into the Queue')
    # Put the result into the queue
    queue.put(answer)

@app.get("/static/{file_uuid}.png")
async def get_image(file_uuid: str):
    """
    Serve a PNG file from the 'static' folder.
    """
    file_path = os.path.join('static', f"{file_uuid}.png")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")
    return {"error": "File not found"}


@app.get("/static/{file_uuid}.mp3")
async def get_image(file_uuid: str):
    """
    Serve a MP3 file from the 'static' folder.
    """
    file_path = os.path.join('static', f"{file_uuid}.mp3")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg")
    return {"error": "File not found"}

@app.get("/static/{file_uuid}.aac")
async def get_image(file_uuid: str):
    """
    Serve a AAC file from the 'static' folder.
    """
    file_path = os.path.join('static', f"{file_uuid}.aac")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/aac")
    return {"error": "File not found"}



def load_profile(full_name: str, preferences: dict, query: str, messages: Any) -> Any:
    profile = LoadProfile(full_name, preferences=preferences)
    profile.load_llm_configurations()
    answer = profile.fastapi_response(query, preferences, messages=messages)
    return answer

@app.post("/query/")
def query(query_request: QueryRequest):
    # Submit the task to the ProcessPoolExecutor and wait for the result
    future = executor.submit(load_profile, query_request.full_name, query_request.model_dump(), query_request.query, query_request.messages)
    result = future.result()  # This will block until the task is complete
    return result




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
  print('Personalization Endpoint Recieved', query_request)
  personlize_agent = BuildPersonalizedProfile(query_request.model_dump(), messages=query_request.messages)
  output = personlize_agent.build_profile()
  print('Personalization Endpoint Returned', output)
  return output


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
  
  
@app.get('/loaderio-ef3a3bddeb682ef12664942c9141c92b.txt')
def loaderio():
    # send the loader.io verification .txt file
    return StreamingResponse(open('loaderio-ef3a3bddeb682ef12664942c9141c92b.txt', 'rb'), media_type='text/plain')
