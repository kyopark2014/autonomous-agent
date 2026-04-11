from strands import Agent
from strands_tools import shell

import os
os.environ["BYPASS_TOOL_CONSENT"] = "true"

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