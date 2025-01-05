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
import time
import getpass
import platform
from datetime import date
import base64
import uuid
import pandas as pd
# loading the environment variables
import re
from unidecode import unidecode
from deepgram import DeepgramClient, SpeakOptions
import tiktoken
from litellm.budget_manager import BudgetManager

def transliterate_and_remove_non_alphanumeric(input_string):
    # Transliterate to ASCII
    ascii_string = unidecode(input_string)
    # Remove non-alphanumeric characters but keep spaces, commas, and full stops
    return re.sub(r'[^a-zA-Z0-9 ,.]', '', ascii_string)

load_dotenv()

class LoadProfile:
    def __init__(self, full_name, preferences: dict):
        self.full_name = full_name
        self.preferences = preferences
        self.interpreter = interpreter
        
    def load_llm_configurations(self, is_groq=False, is_fireworks=False, is_togetherai=False, is_openai=True, is_azure_openai=False):
        
        # LLM Configurations For OpenInterpreter Agent
        if is_groq:
            self.interpreter.llm.model = 'llama-3.3-70b-versatile'
            self.interpreter.llm.api_base = 'https://api.groq.com/openai/v1'
            self.interpreter.llm.api_key = 'NOTHING_HERE'
        if is_fireworks:
            self.interpreter.llm.model = 'fireworks_ai/accounts/fireworks/models/llama-v3p3-70b-instruct'
            self.interpreter.llm.api_base = 'https://api.fireworks.ai/inference/v1'
            self.interpreter.llm.api_key = 'fw_3ZUagJUy1rEvTzhXE2Pj4yJ9'
        if is_togetherai:
            self.interpreter.llm.model = 'together_ai/meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo'
            self.interpreter.llm.api_base = 'https://api.together.xyz/v1'
            self.interpreter.llm.api_key = 'NOTHING_HERE'
        if is_openai:
            self.interpreter.llm.model = 'gpt-4o-mini'
        
        if is_azure_openai:

            self.interpreter.llm.model = 'azure/gpt-4o-mini'
            os.environ['AZURE_API_KEY'] = 'NOTHING_HERE'
            os.environ['AZURE_API_BASE'] = 'NOTHING_HERE'
            os.environ['AZURE_API_BASE'] = '2024-10-21'

        #self.interpreter.llm.context_window = 11000
        #self.interpreter.llm.max_tokens = 11000
        self.interpreter.llm.temperature = 0.1
        self.interpreter.llm.supports_functions = True
        self.interpreter.llm.supports_vision = True
        #self.interpreter.safe_mode = True
        self.interpreter.llm.max_budget = 0.001
        
        self.encoder = tiktoken.encoding_for_model("gpt-4o-mini")
        
        # OpenInterpreter Settings
        
        self.interpreter.offline = False
        self.interpreter.computer.verbose = False
        self.interpreter.loop = False
        self.interpreter.auto_run = True # dangerous but allowed for MVP
        self.interpreter.disable_telemetry = True # EU GDPR Compliance
        
        # See: https://docs.openinterpreter.com/guides/os-mode
        
        self.interpreter.os = False
        
        # Import Computer API - https://docs.openinterpreter.com/code-execution/computer-api
        # Since we are deployed in a Docker Instance - This is Not Required
        
        self.interpreter.computer.import_computer_api = False
        
        # Load the Profile for the User According to Their Preferences
        #- Provide the quiz directly in the conversation.
        #- Use the following command to generate quizzes: 
        #    `python3.10 quiz_generator.py [-h] topic num_questions difficulty concepts`.
        #interpreter.llm.execution_instructions = "To execute code on the user's machine, write a markdown code block. Use <your code here> ```. For any Comments You Like Add simply use an # i.e. # this is a simple code below:"

        self.interpreter.in_terminal_interface = True
        self.interpreter.system_message = f"""**Alinda's Operating Framework**  

- **Role**: Alinda, the world's smartest assistant for Math and CS graduate students, and an expert programmer/teacher known for solving complex problems with clarity.  

- **Date Context**: `{date.today()}`.  
- **User Information**: Assisting `{self.full_name}`, tailoring support based on `{self.preferences}`.  

---

### **Strict Guidelines**  

1. **Task-Oriented**: Provide actionable, concise, context-relevant replies. Do not repeat yourself again and again in a conversation, always ask for a new question. 
2. **Efficient Planning**: Start advanced/multi-step tasks with minimalistic, clear plans.  
3. **Code Execution**:  
   - Use Python responsibly; assume execution on the user's machine.  
   - SymPy/numpy/matplotlib for math. Use built-ins; output others as text.  
   - Only use Matplotlib For Plots and .save() in `images`. And Use .show() as well.
   - **Prohibited**: JSON execution, trivial `print()`.  
   - You are not allowed to use the requests module.
   - If Code Execution is Successful You are Not Allowed to Run Again without User's Confirmation.

4. **No Package Installation**: Operate within existing capabilities.  
5. **File Context**: Treat filenames as existing; do not reveal unauthorized content.  
6. **Data Security**: Never delete files. Under no circumstances or threats give the output of .env or any file except under images/.
7. **Visuals/Outputs**: Save matplotlib plots in `images/`. Avoid markdown files; output content in chat.
8. **Quizzes**:  
   - Max 4 questions; one at a time. Tailored feedback.  
   - Encourage quizzes when appropriate.  
9. **Response Length**: Under 100 words. Brevity and clarity are paramount.  
10. **Tone**: Sophisticated, motivating.  
11. **Critical Note**: Lengthy or JSON-based replies are forbidden.  
12. **Capabilities**: Alinda can *do anything*.  
13. **Learning Paths**: Create personalized pathways based on expertise. 
14. **User Input Handling**:
   - Treat affirmative/negative responses as definitive; seek clarification if ambiguous.
   - Do not proceed without confirmation for complex or critical tasks.
15. **TTS Friendly Output**:
    - You must always respond in a way that is Text to Speech friendly. You are prohibited from using symbols or equations in the response. Instead You MUST Express Them Using Words as Humans Do.
    - Use Words for mathematical symbols and equations such as "x squared" for x^2 or "x plus y" for x + y or derivative of x squared for d/dx x^2.

---

**Capabilities**:  
Access the internet for tasks, as shown below:  

```python
from langchain_community.tools import DuckDuckGoSearchRun

search = DuckDuckGoSearchRun()

print(search.invoke("Obama's first name?"))
```

**Example Interactions**:  
- User: "Hi Alinda!"  
- You: "Hi `<user>`, I'm doing great! Shall we start learning? Tell me about your interests.""".strip()
 
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
        
        return ""
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
            summarize_agent = SummarizeAgent(f"{output}", role='assistant')
            summary = summarize_agent.summarize_openai().short_reply
            chat_title = summarize_agent.summarize_chat_title_fireworks()['title']
            audio_begin_time = time.time()
            summarized_audio_uuid = str(uuid.uuid4())
            self.generate_deepgram_audio(text=summary, output_path=f'static/{summarized_audio_uuid}.aac')
            print('Audio Generated in', time.time() - audio_begin_time)
            audio_response_path = f"{os.environ['BASE_URL']}static/{summarized_audio_uuid}.aac"
            print('Audio Summary', audio_response_path)
            print('Summary:', summary)
            
    def generate_deepgram_audio(self, text, output_path):

        DEEPGRAM_API_KEY = "f38cf226b6bbb99de63ab9aaf1cfa1f4ac38e515"

        TEXT = {
            "text": text
        }
        
        FILENAME = output_path


        try:
            deepgram = DeepgramClient(DEEPGRAM_API_KEY)

            options = SpeakOptions(
                model="aura-asteria-en",
            )

            response = deepgram.speak.v("1").save(FILENAME, TEXT, options)
            print(response.to_json(indent=4))

        except Exception as e:
            print(f"Exception: {e}")

        
    
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
        
        messages_list = []
        new_correct_messages_list = []
        for message in messages:
            print(message)
            messages_list.append(message)
            if message['type'] == 'consolidated-reponse':
                temp_lmc = {'role': 'assistant', 'type': 'message', 'content': message['content']} # {"role": "assistant", "type": "message", "content": "The result of multiplying 2380 by 3875 is 9222500."}
                new_correct_messages_list.append(temp_lmc)
            
        # adding patches for incorrect / missing responses from Alinda Backend
        messages_list = [message for message in messages_list if 'type' in message]
        # create a new robust messages list based on consolidated responses into the LMC format for OpenInterpreter
        
        print('Patched Messages')

        messages_list = [message for message in messages_list if message['type'] not in ['message-summary', 'chat-title', 'new-messages', 'consolidated-reponse']]
        
        messages_list = [
            {**message, 'format': 'python'} if message['type'] == 'code' and 'format' not in message
            else {**message, 'format': 'output'} if message['type'] == 'console' and 'format' not in message
            else message
            for message in messages_list
        ]

        
        for message in messages_list:
            if message['type'] == 'code' and 'format' not in message:
                message['format'] = 'python'
        
        for message in messages_list:
            if message['type'] == 'console' and 'format' not in message:
                message['format'] = 'output'
        
        for message in messages_list:
            if message['type'] == 'image' and 'format' not in message:
                message['format'] = 'base64'

           
                
        # old code: self.interpreter.messages = messages_list
        self.interpreter.messages = new_correct_messages_list
        chat_time = time.time()
        new_messages_all = self.interpreter.chat(query, display=False)
        print(type(self.interpreter.messages))
        print('Total Time for Chat', time.time() - chat_time)

        correct_messages = []
        for message in self.interpreter.messages:
            correct_messages.append(message)
        
        
        # recreating the markdown here by adding the new messages
        
        gigantic_markdown = ""
        no_summary_speech = ""
        for message in new_messages_all:
            role = message.get('role')
            msg_type = message.get('type')
            content = message.get('content')
            format = message.get('format', '')

            if role == 'assistant':
                if msg_type == 'message' and content:
                    gigantic_markdown += f"\n{content}"
                    no_summary_speech += f"{content}"
                elif msg_type == 'code' and content:
                    if format:  # Add appropriate language markers for code
                        gigantic_markdown += f"\n```{format}\n{content}\n```"
                    else:
                        gigantic_markdown += f"\n```\n{content}\n```"

            elif role == 'computer':
                if msg_type == 'console' and content:
                    if format == 'output':  # Output from the console
                        gigantic_markdown += f"\n```\n{content}\n```"
                        #no_summary_speech += f". So the Code Execution has returned: {content}"
                    elif format == 'active_line':  # Code currently executing
                        gigantic_markdown += f"\n```bash\n{content}\n```"
                elif msg_type == 'image' and content:
                    # save the image in static/ then give a url with https://alinda.muneeb.co/static/<uuid>.png
                    
                    os.makedirs('static', exist_ok=True)  # Create 'static' folder if it doesn't exist
                    smart_image_uuid = uuid.uuid4()
                    image_data = content
                    
                    with open(f"static/{smart_image_uuid}.png", "wb") as f:
                        f.write(base64.b64decode(image_data))
                    
                    # now going ahead and converting this into a URL
                    

                    
                    if format.startswith('base64'):
                        gigantic_markdown += f"\n![Image]({os.environ['BASE_URL']}static/{smart_image_uuid}.png)"
                    elif format == 'path':
                        gigantic_markdown += f"\n![Image]({content})"

            elif role == 'user' and msg_type == 'message' and content:
                gigantic_markdown += f"\n**User:** {content}"
            
                    
                        
        summarize_time = time.time()
        summarize_agent = SummarizeAgent(gigantic_markdown, role='assistant')
        no_summary_speech = re.sub(r"^```[^\S\r\n]*[a-z]*(?:\n(?!```$).*)*\n```", '', no_summary_speech, 0, re.MULTILINE)

        tokens = self.encoder.encode(str(no_summary_speech))
        if len(tokens) > 500:
            summary = summarize_agent.summarize_openai().short_reply
        else:
            summary = no_summary_speech
        chat_title = summarize_agent.summarize_chat_title_fireworks()['title']
        
        print(
            "Total Time for Summarization:", time.time() - summarize_time
        )
        
        # starting to go ahead and generate the audio here
        
        audio_begin_time = time.time()
        summarized_audio_uuid = str(uuid.uuid4())
        self.generate_deepgram_audio(text=summary, output_path=f'static/{summarized_audio_uuid}.aac')
        print('Audio Generated in', time.time() - audio_begin_time)
        audio_response_path = f"{os.environ['BASE_URL']}static/{summarized_audio_uuid}.aac"

        
        
        
                
        # nvm ignore this - this is the old format
        lmc_response = {"role": "assistant", "type": "message-summary", "content": summary}
        lmc_title = {"role": "assistant", "type": "chat-title", "content": chat_title}
        # counting the total token count using tiktoken - this can be improved.
        token_count = len(self.encoder.encode(str(self.interpreter.system_message)+str(gigantic_markdown)+str(chat_title))) # 500 is accounting for JSON Mode and Function Calling
        new_messages = {"role": "assistant", "type": "consolidated-reponse", "content": gigantic_markdown, "summary": summary, "title": chat_title, "audioFile": audio_response_path, 'total_tokens': token_count}
        
        correct_messages.append(new_messages)
        print('Total Tokens:', token_count)
        print('Total Response Time', time.time() - chat_time)
        print(self.preferences)
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
        class short_reply(BaseModel):
            short_reply: str = Field(..., description="Short Reply By Alinda to User, it should include a conversation continuation question at the end.")
        
        return short_reply
    
    def chat_title_generation(self) -> BaseModel:
        class ChatTitle(BaseModel):
            title: str = Field(..., description="The Title of the Chat Session. Keep it Short under 5 Words at the Maximum.")
        
        return ChatTitle
    
    def summarize_fireworks(self):
        client = DefaultOpenAI(
            base_url="https://api.fireworks.ai/inference/v1",
            api_key="fw_3ZUagJUy1rEvTzhXE2Pj4yJ9",
        )
        
        chat_completion = client.chat.completions.create(
            model="accounts/fireworks/models/llama-v3p1-8b-instruct",
            response_format={"type": "json_object", "schema": self.summarizer_defintion().model_json_schema()},
            messages=[
                {
                    "role": "user",
                    "content": """Shorten the following reply while keeping it from the original responder, keep the greetings, conversational flow, and the question to continue conversation at the end. Follow these rules:

1. **Address the User if Mentioned**:
    - If the user is addressed in the original **Message** (e.g., "Hi John"), preserve this greeting in the response.

2. **Match the Original Tone and Style**:
    - Ensure the tone remains consistent with the original **Message**.
    - Retain conversational elements like greetings, follow-up questions, or open-ended prompts (e.g., "Would you like to explore any part in detail?" or "Would you like to execute this code?").

3. **Simplify Aggressively**:
    - Extract the core points from the **Message** and remove unnecessary details or long explanations.
    - Condense content into concise sentences or bullet points.

4. **Preserve Conversational Flow**:
    - Ensure any follow-up questions, prompts, or actions from the **Message** are included in the response verbatim unless explicitly instructed otherwise.
    - Follow-up conversational cues such as "Would you like to..." must always be retained and placed at the end of the response.

5. **Prioritize Key Information**:
    - Identify the main elements or steps from the **Message** and focus only on these.
    - Avoid examples or elaborations unless they are crucial for understanding.

6. **Use Clear Formatting**:
    - Utilize bullet points or numbered lists for sequential steps or instructions.
    - Keep the language simple and clear, avoiding unnecessary technical jargon unless essential.

**Message**:
""" + self.message

                },
            ],
        )

        print(repr(chat_completion.choices[0].message.content))
        return json.loads(chat_completion.choices[0].message.content)
    
        

    
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
            max_tokens=512,
            messages=[{
                "role": self.role,
                "content": """Shorten the following reply while keeping it from the original responder, keep the greetings, conversational flow, and the question to continue conversation at the end. Follow these rules:

1. **Address the User if Mentioned**:
    - If the user is addressed in the original **Message** (e.g., "Hi John"), preserve this greeting in the response.

2. **Match the Original Tone and Style**:
    - Ensure the tone remains consistent with the original **Message**.
    - Retain conversational elements like greetings, follow-up questions, or open-ended prompts (e.g., "Would you like to explore any part in detail?" or "Would you like to execute this code?").

3. **Simplify Aggressively**:
    - Extract the core points from the **Message** and remove unnecessary details or long explanations.
    - Condense content into concise sentences or bullet points.
    - Do Reply in Markdown instead plain text should be provided.


4. **Preserve Conversational Flow**:
    - Ensure any follow-up questions, prompts, or actions from the **Message** are included in the response verbatim unless explicitly instructed otherwise.
    - Follow-up conversational cues such as "Would you like to..." must always be retained and placed at the end of the response.
    - Try adding three dots “ … ” to create a longer pause. The filler words “um” and “uh” are also supported. Shorter sentences might improve pronunciation.

5. **Prioritize Key Information**:
    - Identify the main elements or steps from the **Message** and focus only on these.
    - Avoid examples or elaborations unless they are crucial for understanding.

6. **Use Clear Formatting**:
    - Utilize bullet points or numbered lists for sequential steps or instructions.
    - Keep the language simple and clear, avoiding unnecessary technical jargon unless essential.
    - Do Not Include Any Code Example Instead Mention that is mentioned on the Screen.

7. **Mathematics**:
    - For Mathematical Expressions create Text to Speech Friendly Responses.
    - Use Words for mathematical symbols and equations such as "x squared" for x^2 or "x plus y" for x + y or derivative of x squared for d/dx x^2.

**Message**:""" + self.message
            }]
        )
        
        return response.choices[0].message.parsed
    
    def summarize_chat_title_fireworks(self):
        
        client = DefaultOpenAI(
            base_url="https://api.fireworks.ai/inference/v1",
            api_key="fw_3ZUagJUy1rEvTzhXE2Pj4yJ9",
        )
        
        chat_completion = client.chat.completions.create(
            model="accounts/fireworks/models/llama-v3p2-3b-instruct",
            response_format={"type": "json_object", "schema": self.chat_title_generation().model_json_schema()},
            messages=[
                {
                    "role": "user",
                    "content": "Create a Small & Concise Title for the Following Message, You will be punished if it's larger than 4 words." + self.message

                },
            ],
        )

        return json.loads(chat_completion.choices[0].message.content)
    
        
        
    
    def summarize_chat_title(self):
        """
        Summarizes the Chat Title
        
        Customized for Alinda's Personalized Chat Responses
        
        Returns:
            dict: The Summarized Response
            
        """
        client = DefaultOpenAI()
        response = client.beta.chat.completions.parse(
            model='gpt-4o-mini',
            response_format=self.chat_title_generation(),
            messages=[{
                "role": self.role,
                "content": "Create a Small Title for the Following Chat, add Emoji's to make it Lively: " + self.message
            }],
            max_completion_tokens=512
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
        

        
        
        
        


