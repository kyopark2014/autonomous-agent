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

## 시스템 프롬프트를 스스로 수정하는 에이전트<img width="850" height="84" alt="image" src="https://github.com/user-attachments/assets/35e5d09b-8802-4e86-90b8-2c1dab9933a6" />


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

## 상호작용에서 학습하는 에이전트

```python
from strands import Agent
from strands_tools import shell, retrieve
from strands_research_agent.tools import store_in_kb

agent = Agent(tools=[shell, retrieve, store_in_kb])

while True:
    user_input = input("\n~ ")
    
    agent.tool.retrieve(
        text=user_input,
        knowledgeBaseId="R1QHGYLBCV"
    )
    result = agent(user_input)
    
    agent.tool.store_in_kb(
        title="Conversation History",
        content=f"User input: {user_input}\nResult: {result}"
    )
```



## Reference 

[AIM426 - Using Strands Agents to Build Autonomous, Self-Improving AI Agents](https://github.com/cagataycali/strands-re-invent)

[AWS re:Invent 2025 - Using Strands Agents to build autonomous, self-improving AI agents (AIM426)](https://www.youtube.com/watch?v=RQfW7eQsXqk)

