from langchain_openai import OpenAI
from langchain_experimental.llm_symbolic_math.base import LLMSymbolicMathChain
from dotenv import load_dotenv
from sympy import symbols, Eq, Function, Derivative, solve
load_dotenv()



llm_symbolic_math = LLMSymbolicMathChain.from_llm(OpenAI(max_tokens=2000, temperature=0), allow_dangerous_requests=True)

print(llm_symbolic_math("What is the derivative of x^2?"))