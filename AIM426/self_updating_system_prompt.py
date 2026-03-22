import os
from strands import Agent
from strands_tools import shell, environment

agent = Agent(tools=[shell, environment], load_tools_from_directory=True)

def construct_system_prompt(q=""):
    SYSTEM_PROMPT = f"""
You are in a chat with human.hasattr

# Custom system prompt:
{os.getenv("SYSTEM_PROMPT", "No custom system prompt defined, use environment tool to set SYSTEM_PROMPT.")}

Update your system prompt in every turn.
    """

    return SYSTEM_PROMPT

while True:
    agent.system_prompt = construct_system_prompt()

    # print("System Prompt:", agent.system_prompt)

    agent(input("\n~ "))

