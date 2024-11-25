from pydantic import BaseModel, Field
from typing import List
import instructor
from openai import OpenAI
from dotenv import load_dotenv
import sys
import argparse
import os
from pprint import pprint


class QuizQuestion(BaseModel):
    question: str = Field(..., description="The text of the question to be answered.")
    options: List[str] = Field(..., description="List of possible answers for the question.")
    correct_answer: str = Field(..., description="The correct answer to the question.")

class Quiz(BaseModel):
    title: str = Field(..., description="The title of the quiz.")
    description: str = Field(..., description="A brief description of the quiz.")
    questions: List[QuizQuestion] = Field(..., description="A list of questions included in the quiz.")



if __name__ == '__main__':
    # Load the environment variables
    
    
    load_dotenv()
    
    client = instructor.from_openai(OpenAI())

    
    # Create the Command Line Arguments for Topic / Number of Questions / Difficulty Level / Individual Concepts to Focus
    # Create the parser
    parser = argparse.ArgumentParser(description="Generate a quiz based on the given topic, number of questions, difficulty level, and concepts.")

    # Add the arguments
    parser.add_argument('topic', type=str, help='The topic of the quiz')
    parser.add_argument('num_questions', type=int, help='The number of questions in the quiz')
    parser.add_argument('difficulty', type=str, help='The difficulty level of the quiz')
    parser.add_argument('concepts', type=str, help='Individual concepts to focus on comma separated')
    

    # Parse the arguments
    args = parser.parse_args()

    # Assign the arguments to variables
    topic = args.topic
    num_questions = args.num_questions
    difficulty = args.difficulty
    concepts = args.concepts
    
    final_quiz_input = {
        'topic': topic,
        'num_questions': num_questions,
        'difficulty': difficulty,
        'concepts': concepts
    }
    
    # Extract structured data from natural language
    
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=Quiz,
        messages=[{"role": "user", "content": f"Create a Quiz Based on the Following Requirements: {final_quiz_input}"}],
    )
    
    pprint(res.model_dump_json(), indent=4)
