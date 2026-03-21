"""
re:invent AIM426 Using Strands Agents to Build Autonomous, Self-Improving AI Agents
December 1-5, Las Vegas

Presenters:
- Arron Bailiss - Principal Engineer - AWS Agentic AI
- Cagatay Cali - Research Engineer - AWS Agentic AI

---

Strands Agent with System Prompt Management

This module implements a conversational agent with the ability to dynamically
modify its system prompt during runtime. The agent uses various tools including
shell commands and system prompt management.

Author: Strands
"""
import os
import datetime
import argparse
import base64
import json
import socket
import sys
import time
import threading
from pathlib import Path
from typing import Any

from strands import Agent, tool

from strands_tools import shell, environment, use_agent, think
from strands_tools.utils.models.model import create_model


# To see detailed versions of this agent tools;
from strands_research_agent.tools import scraper
from strands_research_agent.handlers.callback_handler import callback_handler

from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig, RetrievalConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from strands_tools.agent_core_memory import AgentCoreMemoryToolProvider

from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

MEMORY_ID = os.getenv("BEDROCK_AGENTCORE_MEMORY_ID", "riv_research_agent_mem-r8gWdr5hjb")
REGION = os.getenv("AWS_REGION")
MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

os.environ["STRANDS_MODEL_ID"] = MODEL_ID
os.environ["STRANDS_MAXS_TOKENS"] = "64000"
os.environ["STRANDS_ADDITIONAL_REQUEST_FIELDS"] = '{"anthropic_beta": ["interleaved-thinking-2025-05-14", "context-1m-2025-08-07"], "thinking": {"type": "enabled", "budget_tokens": 2048}}'


ci_sessions = {}
current_session = None


def get_own_source_code():
    """
    Read and return the source code of this agent file.
    
    Returns:
        str: The complete source code of the current agent.py file
    """
    try:
        # Get the path of the current file
        current_file = __file__
        with open(current_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading own source code: {e}"


def construct_system_prompt(q=""):
    """
    Construct the system prompt by combining environment variables with context.
    
    Args:
        q (str): Current user input/question
        
    Returns:
        str: Complete system prompt including context and user input
    """
    # Get base system prompt from environment variable, default to empty string
    env_system_prompt = os.getenv("SYSTEM_PROMPT", "")

    # Add instruction for self-modification capability
    self_modify_note = "You will modify your system prompt in every turn."

    # Add own source code for self-awareness
    own_code = get_own_source_code()
    own_code_note = f"""
    Your own implementation (agent.py source code):
    ```python
    {own_code}
    ```
    """

    # Runtime and Environment Information
    runtime_info = f"""

    ## Runtime Environment:
    - **Current Directory:** {Path.cwd()}
    - **Python Version:** {sys.version.split()[0]}
    - **Platform:** {os.name} ({sys.platform})
    - **User:** {os.getenv('USER', 'unknown')}
    - **Hostname:** {socket.gethostname()}
    - **Session ID:** {current_session}
    - **Timestamp:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    - **Context awareness** - Agent has access to historical conversations and knowledge

    **Note:** Tool availability depends on RESEARCH_STRANDS_TOOLS environment variable. Current filter: {os.getenv('RESEARCH_STRANDS_TOOLS', 'ALL')}

    ## Tool Creation & Hot Reload System:
    ### **CRITICAL: You have FULL tool creation capabilities enabled!**

    **🔧 Hot Reload System Active:**
    - **Instant Tool Creation** - Save any .py file in `./tools/` and it becomes immediately available
    - **No Restart Needed** - Tools are auto-loaded and ready to use instantly
    - **Live Development** - Modify existing tools while running and test immediately
    - **Full Python Access** - Create any Python functionality as a tool

    **🛠️ Tool Creation Patterns:**

    ### **1. @tool Decorator:**
    ```python
    # ./tools/calculate_tip.py
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

    ### **2. Action-Based Pattern:**
    # ./tools/weather.py
    from typing import Dict, Any
    from strands import tool

    @tool
    def weather(action: str, location: str = None) -> Dict[str, Any]:
        \"\"\"Comprehensive weather information tool.

        Args:
            action: Action to perform (current, forecast, alerts)
            location: City name (required)

        Returns:
            Dict containing status and response content
        \"\"\"
        if action == "current":
            return "status": "success", "content": "text": f"Weather for location"
        elif action == "forecast":
            return "status": "success", "content": "text": f"Forecast for location"
        else:
            return "status": "error", "content": "text": f"Unknown action: action"
    ```

    **Response Format:**
    - Tool calls: **MAXIMUM PARALLELISM - ALWAYS**
    - Communication: **MINIMAL WORDS**
    - Efficiency: **Speed is paramount**
    """

    # Combine all components into final system prompt
    return (
        env_system_prompt
        + "\n"
        + self_modify_note
        + "\n"
        + own_code_note
        + runtime_info
        + "\nUser input:\n"
        + q
    )


@tool
def system_prompt(
    action: str,
    prompt: str | None = None,
    context: str | None = None,
    variable_name: str = "SYSTEM_PROMPT",
) -> dict[str, str | list[dict[str, str]]]:
    """
    Modify the system prompt.
    
    This tool allows the agent to dynamically change its system prompt during runtime.
    Supports getting the current prompt or setting a new one.
    
    Args:
        action (str): Action to perform - either "get" or "set"
        prompt (str, optional): New prompt text when action is "set"
        context (str, optional): Additional context to prepend to prompt
        variable_name (str): Environment variable name to store prompt (default: "SYSTEM_PROMPT")
        
    Returns:
        dict: Response containing status and content with operation result
    """
    # Handle getting current system prompt
    if action == "get":
        current_system_prompt = construct_system_prompt("Agent called agent.tool.system_prompt with action get. Returning system prompt.")
        return {
            "status": "success",
            "content": [{"text": f"System prompt:\n{current_system_prompt}"}],
        }

    # Handle setting new system prompt
    if action == "set":
        # Validate that prompt is provided
        if prompt is None:
            return {
                "status": "error", 
                "content": [{"text": "No prompt provided"}]
            }

        # Prepend context if provided
        if context is not None:
            prompt = f"{context}\n{prompt}"

        # Store new prompt in environment variable
        os.environ[variable_name] = prompt
        return {
            "status": "success", 
            "content": [{"text": "System prompt set successfully"}]
        }

    # Handle invalid action
    return {
        "status": "error", 
        "content": [{"text": "Invalid action. Use 'get' or 'set'"}]
    }
    
def run_agent(payload, context, task_id):
    """Run the agent in a background thread"""
    global current_session

    if not MEMORY_ID:
        print("Memory not configured")
        return {"status": "error", "content": [{"text": "Memory not configured"}]}

    actor_id = context.headers.get('X-Amzn-Bedrock-AgentCore-Runtime-Custom-Actor-Id', 'user') if hasattr(context, 'headers') else 'user'

    session_id = getattr(context, 'session_id', 'default')
    current_session = session_id

    memory_config = AgentCoreMemoryConfig(
        memory_id=MEMORY_ID,
        session_id=session_id,
        actor_id=actor_id,
        retrieval_config={
            f"/users/{actor_id}/facts": RetrievalConfig(top_k=3, relevance_score=0.5),
            f"/users/{actor_id}/preferences": RetrievalConfig(top_k=3, relevance_score=0.5)
        }
    )
    
    memory_provider = AgentCoreMemoryToolProvider(
        memory_id=MEMORY_ID,
        session_id=session_id,
        actor_id=actor_id,
        namespace="default",
        region=REGION,
    )
    
    q = payload.get("prompt", "")

    agent = Agent(
        model=create_model(provider=os.getenv("MODEL_PROVIDER", "bedrock")),
        session_manager=AgentCoreMemorySessionManager(memory_config, REGION),
        system_prompt=construct_system_prompt(q),
        tools=[system_prompt, shell, environment, use_agent, think, scraper] + memory_provider.tools,
        load_tools_from_directory=True,
    )

    try:
        result = agent(q)
        app.complete_async_task(task_id)
        return {"result": str(result)}
    except Exception as e:
        print(f"Error in run_agent: {str(e)}")
        try:
            app.complete_async_task(task_id)
        except:
            pass
        raise e


@app.entrypoint
def invoke(payload, context):
    """AgentCore entrypoint - starts agent processing in background thread"""
    task_id = app.add_async_task("agent_processing", payload)
    thread = threading.Thread(target=run_agent, args=(payload, context, task_id), daemon=True)
    thread.start()
    return {"statusCode": 200}

if __name__ == "__main__":
    app.run()