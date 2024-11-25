import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import DuckDuckGoSearchRun, BingSearchResults, GoogleSearchRun

search = DuckDuckGoSearchRun()
search_google = GoogleSearchRun()



load_dotenv()

llm = ChatOpenAI(model='gpt-4o-mini')

print(search_google.invoke("MongoDB NoSQL Insert Example?"))

