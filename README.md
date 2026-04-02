# Autonomous Agent

## 기본 에이전트

```python
from strands import Agent
from strands_tools import shell

agent = Agent(tools=[shell])

# agent("What can you do?")
agent("너는 무엇을 할 수 있어?")
```

## Self Updating System Prompt

```python
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
```




## Reference 

[AIM426 - Using Strands Agents to Build Autonomous, Self-Improving AI Agents](https://github.com/cagataycali/strands-re-invent)

[AWS re:Invent 2025 - Using Strands Agents to build autonomous, self-improving AI agents (AIM426)](https://www.youtube.com/watch?v=RQfW7eQsXqk)

