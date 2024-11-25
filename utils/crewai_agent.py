# patching the sqlite3 module

from crewai_tools import ScrapeWebsiteTool, FileWriterTool, TXTSearchTool, WebsiteSearchTool
from crewai import Agent, Task, Crew, Process
import os
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain_experimental.llm_symbolic_math.base import LLMSymbolicMathChain
from crewai_tools import CodeInterpreterTool
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_community.callbacks import get_openai_callback

# Load environment variables from the .env file
load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')

# loading the LLMs

gpt_4o_mini = OpenAI(model="gpt-4o-mini", temperature=0.1)


# Loading and Testing the Tools

website_scrape_tool = ScrapeWebsiteTool()  
file_writer_tool = FileWriterTool()
txt_search_tool = TXTSearchTool()
website_search_tool = WebsiteSearchTool()
llm_symbolic_math = LLMSymbolicMathChain.from_llm(OpenAI(max_tokens=2000, temperature=0), allow_dangerous_requests=True)

# loading the human in the loop

human = load_tools(['human'] )


# Creating the Agent

alinda = Agent(
  role='alinda_ai',
  goal='''To provide tutoring services to students on various topics, with a focus on mathematics and computer science. It's Job is to talk with other agents and give tasks to solve and then provide a final output to user in a simple way.''',
  backstory='Alinda is an AI-powered Voice Assistant Tutor. She specializes in tutoring students on various topics, with a focus on mathematics and symbolic computation. She is also capable of conversational tutoring in a friendly and interactive manner.',
  llm = gpt_4o_mini,
  allow_delegation=True,
  verbose=True)

maths_computer = Agent(
    role='maths_computer',
    goal='Provide solutions to symbolic & standard mathematical problems by using the Sympy library.',
    backstory="A Calculator that Solves Single Line Symbolic Math Problems. It needs to be provided with clear instructions along with the equation.",
    llm=llm_symbolic_math,
    allow_delegation=False,
    verbose=True)

# Creating the Tasks


collect_question = Task(
    name='collect_question',
    description='Collecting the question from the user to understand what the user wants to solve. The question should be related to the topic of the conversation.',
    agent=alinda,
    expected_output='''Understand the user's question and provide the user with the next steps to solve the question.''',
    verbose=True,
    human_input=True,
    )


collect_experience = Task(
    name='collect_experience',
    description='Collecting experience & question that user wants answered from the user to understand where the stand in understanding / solving the topic. Maximum 3 Questions and one word answers only.',
    tools=[website_scrape_tool],
    agent=alinda,
    expected_output='''Understand the user's experience level and provide the user with the next steps to improve their understanding of the topic.''',
    verbose=True,
    human_input=True,
    )

solve_equation = Task(
    name='solve_equation',
    agent=maths_computer,
    description='Solving the given equation using the Sympy library. Alinda may need to talk multiple times with the Maths Computer to solve the equation.',
    expected_output='''This Tasks Job is to Solve the Equation and provide the final output to the user in a simple way. Along with Steps to solve the equation.''',
    
    verbose=True
    )

# Creating the Crew

alinda_crew = Crew(
    name='alinda_crew',
    agents=[alinda, maths_computer],
    tasks=[collect_experience, solve_equation],
    process=Process.sequential,
    verbose=True
    )

# Running the Crew
with get_openai_callback() as cb:
    output = alinda_crew.kickoff(inputs={'question': 'What is the derivative of x^2?'})
    print(output)
    print(cb)



