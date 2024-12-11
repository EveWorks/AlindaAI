import os
import sys
import chainlit as cl
from chainlit.input_widget import Select
from alinda_agent import LoadProfile

# Global variable to store the user's profile and preferences
profile = None

class CustomStdout:
    """Redirect stdout to Chainlit UI."""
    def __init__(self, original_stdout):
        self.original_stdout = original_stdout

    def write(self, data):
        if data.strip():  # Only process non-empty outputs
            cl.run_sync(cl.Message(content=data).send())
        self.original_stdout.write(data)

    def flush(self):
        self.original_stdout.flush()

class CustomStdin:
    """Handle input from the Chainlit UI."""
    def __init__(self, original_stdin):
        self.original_stdin = original_stdin

    def readline(self):
        user_response = cl.run_sync(cl.AskUserMessage(content="").send())
        return user_response["content"]

    def flush(self):
        self.original_stdin.flush()


@cl.on_chat_start
async def start():
    """Initialize the agent when a chat session starts."""
    global profile

    sys.stdout = CustomStdout(sys.__stdout__)
    sys.stdin = CustomStdin(sys.__stdin__)

    # Ask user for model selection and user preferences
    model_select = Select(
        id="model",
        label="OpenAI - Model",
        values=["gpt-3.5-turbo", "gpt-4", "gpt-4o-mini"],
        initial_index=2,
    )
    model_settings = await cl.ChatSettings([model_select]).send()

    await cl.Message(content="Please provide your profile details (e.g., name, interests, etc.)").send()
    user_preferences = {
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

    # Process user preferences and initialize the profile
    profile = LoadProfile(full_name="Muneeb Ahmad", preferences=user_preferences)
    profile.load_llm_configurations()
    await cl.Message(content=f"Profile initialized with model: {model_settings['model']}").send()


@cl.on_settings_update
async def setup_agent(settings):
    """Handle settings updates."""
    if profile:
        profile.interpreter.llm.model = settings["model"]
        profile.interpreter.max_output = 1000
        await cl.Message(content=f"Model updated to {settings['model']}").send()


@cl.on_message
async def main(message: cl.Message):
    """Process user messages and send agent responses."""
    if not profile:
        await cl.Message(content="Profile not initialized. Please restart the chat.").send()
        return

    # Process file uploads if any
    if message.elements:
        for element in message.elements:
            file_name = element.name
            content = element.content
            with open(file_name, "wb") as file:
                file.write(content)
            profile.interpreter.computer.run("python", f"User uploaded file: {file_name}")

    # Pass the user query to the agent
    responses = profile.interpreter.chat(message.content, display=True)
    await cl.Message(content=responses).send()

    for response in responses:
        if response['type'] == 'message':
            await cl.Message(content=response['content']).send()
        if response['type'] == 'file':
            await cl.File(content=response['content']).send()
        if response['type'] == 'image':
            from uuid import uuid4
            await cl.Image(url=f"data:image/png;base64,{response['content']}", for_id=str(uuid4())).send()
        if response['type'] == 'console':
            await cl.Message(content=response['content']).send()
        if response['type'] == 'error':
            await cl.Message(content=response['content']).send()
            
    #await cl.Message(content=f"Agent response:\n{response}").send()
