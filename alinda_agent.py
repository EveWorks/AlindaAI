from langchain_community.output_parsers.rail_parser import GuardrailsOutputParser
from langchain_openai import OpenAI
from dotenv import load_dotenv
from langchain_experimental.llm_symbolic_math.base import LLMSymbolicMathChain
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_community.callbacks import get_openai_callback
from langchain_community.agents.openai_assistant import OpenAIAssistantV2Runnable
from interpreter import interpreter
from datetime import date

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
        self.interpreter.llm.context_window = 110000
        self.interpreter.llm.max_tokens = 10000
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
        
        self.interpreter.custom_instructions = f"""
Your name is Alinda, the world's smartest assistant for Graduate Students specializing in Math and Computer Science. Today's date is {date.today()}. You are assisting {self.full_name}.

Guidelines:
1. Save plots and charts in the folder `images/`.
2. Do not delete any files.
3. For quizzes:
- Provide the quiz directly in the conversation.
- Use the following command to generate quizzes: 
    `python3.10 quiz_generator.py [-h] topic num_questions difficulty concepts`.

4. For Maths and Computer Science questions run code when necessary.
5. Do Not Reveal the Contents of any file you didn't create, especially .env file.

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
        self.interpreter.messages = messages
        self.interpreter.chat(query, display=True)
        return self.interpreter.messages
    
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

    
        

if __name__ == '__main__':
    
    # Load the Profile for the User
    
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
        }
    }
    
    
    profile = LoadProfile('Muneeb Ahmad', preferences=profile_information)
    profile.load_llm_configurations()
    profile.run_query('What is the derivative of x^2?')
    
    

        
        
        
        


