from langchain_openai import OpenAI
from langchain_experimental.llm_symbolic_math.base import LLMSymbolicMathChain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory.buffer import ConversationBufferMemory
from dotenv import load_dotenv
import chainlit as cl

# Load environment variables
load_dotenv()

# Initialize the Symbolic Math Agent

# Define Alinda's prompt template
alinda_prompt_template = """
You are "Alinda", an AI-powered Voice Assistant Tutor. You specialize in tutoring 
students on various topics, with a focus on mathematics and symbolic computation. 
You are also capable of conversational tutoring in a friendly and interactive 
manner.

Chat History: {chat_history}
Question: {question}
Answer:"""

prompt_template = PromptTemplate(
    input_variables=["chat_history", "question"],
    template=alinda_prompt_template
)

from typing import Optional
import chainlit as cl

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin@eve.works", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None

# Initialize chat with Chainlit decorator
@cl.on_chat_start
def initialize_chat():
    llm_symbolic_math = LLMSymbolicMathChain.from_llm(
    OpenAI(max_tokens=2000, temperature=0), allow_dangerous_requests=True
    )

    # Initialize the general OpenAI model
    llm = OpenAI(model="gpt-4o-mini", temperature=0)
    conversation_memory = ConversationBufferMemory(
        memory_key="chat_history",
        max_len=50,
        return_messages=True
    )
    
    # Create the main LLM chain
    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt_template,
        memory=conversation_memory
    )
    
    # Store the LLM and Symbolic Math Chain in the session
    cl.user_session.set("llm_chain", llm_chain)
    cl.user_session.set("symbolic_math", llm_symbolic_math)

# Handle incoming user messages
@cl.on_message
async def handle_message(message: cl.Message):
    # Retrieve both chains from the session
    llm_chain = cl.user_session.get("llm_chain")
    symbolic_math = cl.user_session.get("symbolic_math")
    
    # Determine whether the query is math-related
    if "math" in message.content.lower() or "=" in message.content or "solve" in message.content.lower():
        try:
            # Process the query with the symbolic math chain
            response = symbolic_math.invoke(message.content)
            await cl.Message(response["answer"]).send()
        except Exception as e:
            await cl.Message(f"An error occurred: {e}").send()
    else:
        # Process the query with the general LLM chain
        response = await llm_chain.acall(message.content, callbacks=[
            cl.AsyncLangchainCallbackHandler()
        ])
        await cl.Message(response["text"]).send()
