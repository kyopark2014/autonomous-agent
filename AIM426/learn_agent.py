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
