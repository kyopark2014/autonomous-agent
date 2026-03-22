from strands import Agent
from strands_tools import shell

agent = Agent(tools=[shell])

# agent("What can you do?")
agent("너는 무엇을 할 수 있어?")