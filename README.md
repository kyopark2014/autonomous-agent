# Autonomous Agent

## 기본 에이전트

```python
from strands import Agent
from strands_tools import shell

agent = Agent(tools=[shell])

# agent("What can you do?")
agent("너는 무엇을 할 수 있어?")
```

## 도구를 스스로 만드는 에이전트

```python
from strands import Agent
from strands_tools import shell

SYSTEM_PROMPT = """
Goal: Create tool for yourself and start using them directly.

# ./tools/weather.py
from strands import tool

@tool
def calculate_tip(amount: float, percentage: float = 15.0) -> str:
    \"\"\"Calculate tip and total for a bill.
    
    Args:
        amount: Bill amount in dollars
        percentage: Tip percentage (default: 15.0)
        
    Returns:
        str: Formatted tip calculation result
    \"\"\"
    tip = amount * (percentage / 100)
    total = amount + tip
    return f"Tip: tip:.2f, Total: total:.2f"
"""

agent = Agent(tools=[shell], system_prompt=SYSTEM_PROMPT, load_tools_from_directory=True)

agent("Create 5 tool for yourself and start using.")
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

