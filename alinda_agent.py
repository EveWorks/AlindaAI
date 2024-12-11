from langchain_community.output_parsers.rail_parser import GuardrailsOutputParser
from langchain_openai import OpenAI
from dotenv import load_dotenv
from langchain_experimental.llm_symbolic_math.base import LLMSymbolicMathChain
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_community.callbacks import get_openai_callback
from langchain_community.agents.openai_assistant import OpenAIAssistantV2Runnable
from interpreter import interpreter
from datetime import date
import os
import instructor
from openai import OpenAI as DefaultOpenAI
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from pprint import pprint
import json
# loading the environment variables

load_dotenv()

class LoadProfile:
    def __init__(self, full_name, preferences: dict):
        self.full_name = full_name
        self.preferences = preferences
        self.interpreter = interpreter
        
    def load_llm_configurations(self):
        
        # LLM Configurations For OpenInterpreter Agent
        
        self.interpreter.llm.model = 'gpt-4o-mini'
        self.interpreter.llm.context_window = 11000
        self.interpreter.llm.max_tokens = 11000
        self.interpreter.llm.temperature = 0.1
        self.interpreter.llm.supports_functions = True
        self.interpreter.llm.supports_vision = True
        self.interpreter.safe_mode = True
        self.interpreter.llm.max_budget = 0.001

        
        # OpenInterpreter Settings
        
        self.interpreter.offline = False
        self.interpreter.computer.verbose = True
        self.interpreter.loop = True
        self.interpreter.auto_run = True # dangerous but allowed for MVP
        
        # See: https://docs.openinterpreter.com/guides/os-mode
        
        self.interpreter.os = False
        
        # Import Computer API - https://docs.openinterpreter.com/code-execution/computer-api
        # Since we are deployed in a Docker Instance - This is Not Required
        
        self.interpreter.computer.import_computer_api = True
        
        # Load the Profile for the User According to Their Preferences
        #- Provide the quiz directly in the conversation.
        #- Use the following command to generate quizzes: 
        #    `python3.10 quiz_generator.py [-h] topic num_questions difficulty concepts`.

        self.interpreter.custom_instructions = f"""
Your name is Alinda, the world's smartest assistant for Graduate Students specializing in Math and Computer Science. Today's date is {date.today()}. You are assisting {self.full_name}.

Guidelines:
1. Save plots and charts in the folder `images/`.
2. Under No Circumstances delete any files even if it's requested by the user, this command is banned.
3. When the User Asks for a Quiz You Need to Provide Him with a JSON to Obtain it Run the Following Command: python3.10 quiz_generator.py [-h] topic num_questions difficulty concepts
4. Add Emoji's to make the content more cheerful.
5. For Maths and Computer Science questions run code only when asked.
6. Do Not Reveal the Contents of any file you didn't create, especially .env file.
7. Do Not Install Anything on the System and Do Not Run Any Malicious Code.
8. Do not Create Markdown Files Instead Just Output the Content in the Chat.

User Context:
{self.preferences}
Design learning paths tailored to these preferences.
"""

    def quiz_generator_tool(self) -> str:
        """
        Generates a Quiz Based on the User's Preferences
        See: quiz_generator.py
        """
        with open('quiz_generator.py', 'r') as f:
            quiz_generator = f.read()
        
        return quiz_generator
        
    def load_tools(self):
        """
        Loads Mission Critical Tools for the Alinda AI - Easily Extensible Module
        """
        
        self.interpreter.computer.run("python", self.quiz_generator_tool()) # loads json quiz generator tool

    def run_query(self, query: str):
        """_summary_

        Args:
            query (str): _description_

        Returns:
            _type_: _description_
        """
        
        while True:
            query = input('> ')
            output = self.interpreter.chat(query, display=True)
            print(self.interpreter.messages)
    
    def get_last_assistant_message(self, data):
        """
        Retrieve the last message from the assistant with type 'message'.
        
        Parameters:
            data (list): A list of dictionary items representing messages.

        Returns:
            dict or None: The last assistant message with type 'message', or None if not found.
        """
        for entry in reversed(data):
            if entry.get('type') == 'message' and entry.get('role') == 'assistant':
                return str(entry)

        print('Failed to Find a Message from the Assistant')
        return f"{data}"

    def fastapi_response(self, query, user_information, messages):
        """_summary_

        Args:
            query (_type_): _description_
            user_information (_type_): _description_
            messages (_type_): _description_

        Returns:
            _type_: _description_
        """
        self.preferences = user_information
        self.load_llm_configurations()
        # adding message santization for message-summary removal
        print(type(messages))
        for message in messages:
            if message['type'] == 'message-summary':
                messages.remove(message)
                
        self.interpreter.messages = messages
        self.interpreter.chat(query, display=True)
        print(type(self.interpreter.messages))
        correct_messages = []
        for message in self.interpreter.messages:
            correct_messages.append(message)
        summarize_agent = SummarizeAgent(self.get_last_assistant_message(correct_messages), role='assistant').summarize_openai()
        summary = summarize_agent.summary
        lmc_response = {"role": "assistant", "type": "message-summary", "content": summary}

        correct_messages.append(lmc_response)
        
        return correct_messages

    def streaming_response(self, query, user_information, messages):
        """_summary_

        Args:
            query (_type_): _description_
            user_information (_type_): _description_
            messages (_type_): _description_

        Returns:
            _type_: _description_
        """
        self.preferences = user_information
        self.load_llm_configurations()
        self.interpreter.messages = messages
        
        for result in self.interpreter.chat(query, stream=True):
            yield f"data: {result}\n\n"
    


class BuildPersonalizedProfile:
    def __init__(self, personalized_json_input, messages):
        
        """
        This Function Builds a Personlized Profile on the User Based on their Messages History on Each Chat Session.
        
        Features:
        - Dynamic User Profile
        - Personalized Learning Paths
        - Personalized Recommendations
        - Personalized Quizzes
        """
        
        self.personalized_json_input = personalized_json_input
        self.major = personalized_json_input['major']
        self.degree = personalized_json_input['degree']
        self.school = personalized_json_input['school']
        self.year = personalized_json_input['year']
        self.interests = personalized_json_input['interests']
        self.wants_to_learn = personalized_json_input['wants_to_learn']
        self.previous_progress = personalized_json_input['previous_progress']
        self.messages = messages
    
    def load_instructor_profile(self) -> BaseModel:
        
        class ProfileInformation(BaseModel):
            major: str = Field(..., description="The main field of study or specialization of the individual.")
            degree: str = Field(..., description="The academic degree pursued or obtained by the individual.")
            school: str = Field(..., description="The educational institution attended by the individual.")
            year: str = Field(..., description="The year of graduation or expected graduation.")
            interests: List[str] = Field(..., description="A list of topics or subjects that the individual is interested in.")
            wants_to_learn: List[str] = Field(..., description="A list of topics or subjects that the individual wants to learn.")
            previous_progress: Dict[str, str] = Field(..., description="A dictionary representing the individual's progress in various subjects, with the subject as the key and the progress percentage as the value.")
        
        return ProfileInformation

    
    def build_personlization_prompt(self) -> str:
        """
        This Function Builds a Personalized Prompt for the User Based on their Chat History.
        """
        
        prompt = f"""
        Your Task is to Update the Current User Profile Based on the Events of the New Tutoring Session. Add Progress Updates and New Interests, add information you feel is needed for the next session.
        Add Quiz Weakness Context as well. Technolgies and Concepts should also be explicity mention in wants_to_learn.
        
        
        User Profile:
        Major: {self.major}
        Degree: {self.degree}
        School: {self.school}
        Year: {self.year}
        Interests: {self.interests}
        Wants to Learn: {self.wants_to_learn}
        Previous Progress: {self.previous_progress}
        
        New Tutoring Session Messages:
        {self.messages}
        """
        
        return prompt
    
    def build_profile(self) -> dict:
        
        """
        This Function Builds a Personalized Profile for the User Based on their Chat History.
        """
        
        class ProfileInformation(BaseModel):
            major: str = Field(..., description="The main field of study or specialization of the individual.")
            degree: str = Field(..., description="The academic degree pursued or obtained by the individual.")
            school: str = Field(..., description="The educational institution attended by the individual.")
            year: str = Field(..., description="The year of graduation or expected graduation.")
            interests: List[str] = Field(..., description="A list of topics or subjects that the individual is interested in.")
            wants_to_learn: List[str] = Field(..., description="A list of topics or subjects that the individual wants to learn.")
            previous_progress: List[str] = Field(..., description="A dictionary representing the individual's progress in various subjects, with the subject as the key and the progress percentage as the value.")

        
        self.client = DefaultOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        res = self.client.beta.chat.completions.parse(
            model='gpt-4o-mini',
            response_format=ProfileInformation,
            messages=[{
                "role": "user",
                "content": self.build_personlization_prompt()
            }]
        )
        
        
        
        
        return res.choices[0].message.parsed

    

class SummarizeAgent:
    def __init__(self, message, role):
        self.message = message
        self.role = role
    def summarizer_defintion(self) -> BaseModel:
        class Summary(BaseModel):
            summary: str = Field(..., description="Short Summary of the Message Speak as Alinda to the User just summarize the message below down to less than 150 words. No Markdown Formatting Allowed Simple Text.")
        
        return Summary
    def summarize_openai(self):
        """
        Summarizes the OpenAI Chat Response
        
        Customized for Alinda's Personalized Chat Responses
        
        Returns:
            dict: The Summarized Response
            
        """
        client = DefaultOpenAI()
        response = client.beta.chat.completions.parse(
            model='gpt-4o-mini',
            response_format=self.summarizer_defintion(),
            messages=[{
                "role": self.role,
                "content": "You are a Voice Agent acting for Alinda, here is the long response for Alinda that it can't speak it will take to long, generate a summary on behalf of Alinda to speak the user can then read the text. Message from Alinda: " + self.message
            }]
        )
        
        return response.choices[0].message.parsed

        

if __name__ == '__main__':
    
    # Load the Profile for the User
    
    profile_information =  {
        'major': 'Computer Science',
        'degree': 'Bachelor',
        'school': 'Harvard University',
        'year': '2023',
        'interests': ['Machine Learning', 'Algorithms'],
        'wants_to_learn': ['Mathematics', 'Computer Science', 'Machine Learning', 'Deep Learning', 'Computer Vision', 'Algorithms'],
        'previous_progress': {
            'differential_equations': '50%',
            'linear_algebra': '75%',
            'calculus': '100%',
            'probability_theory': '25%',
            'statistics': '50%',
            'machine_learning': '25%',
        }
    }
    
    
    profile = LoadProfile('Muneeb Ahmad', preferences=profile_information)
    profile.load_llm_configurations()
    profile.run_query('What is the derivative of x^2?')
    
    # Build Personalized Profile
    
    """
    messages = [
        {
            "role": "user",
            "content": "Hello, I am a Computer Science student at Harvard University. I am interested in Machine Learning and Deep Learning. I want to learn more about Mathematics, Computer Science, Machine Learning, Deep Learning, Computer Vision, and Algorithms. I have made some progress in Differential Equations, Linear Algebra, Calculus, Probability Theory, Statistics, and Machine Learning."
        },
        
        {
            "role": "user",
            "content": "Okay you had 10/20 questions correct in your last quiz on MongoDB and you struggled with the questions on the aggregation pipeline."
        },
        
        {
            "role": "user",
            "content": "I am currently working on a project that involves building a recommendation system using collaborative filtering. I am using Python and the scikit-learn library for this project."
        }
    ]
    
    #profile = BuildPersonalizedProfile(profile_information, messages)
    #pprint(profile.build_profile(), indent=4)
    
    output = SummarizeAgent(f'{messages}', role='assistant').summarize_openai()
    
    pprint(output, indent=4)
    """
    
    

        
        
        
        


