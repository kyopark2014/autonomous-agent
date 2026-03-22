from strands import Agent
from strands_tools import shell, use_agent, think, swarm, graph, journal

agent = Agent(tools=[shell, use_agent, think, swarm, graph, journal])

while True:
    agent(input("\n~ "))

