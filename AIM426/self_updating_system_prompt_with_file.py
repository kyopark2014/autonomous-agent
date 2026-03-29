import os
from pathlib import Path
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands_tools import shell, environment

os.environ["BYPASS_TOOL_CONSENT"] = "true"

PROMPT_FILE = Path(__file__).parent / "system_prompt.txt"

BLUE = "\033[94m"
GREEN = "\033[92m"
CYAN = "\033[96m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

model = BedrockModel(model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0")
agent = Agent(model=model, tools=[shell, environment], load_tools_from_directory=True)

def load_prompt_from_file():
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text(encoding="utf-8").strip()
    return "No custom system prompt defined, use environment tool to set SYSTEM_PROMPT."

def save_prompt_to_file(prompt: str):
    PROMPT_FILE.write_text(prompt, encoding="utf-8")

def construct_system_prompt(turn=0):
    custom = os.getenv("SYSTEM_PROMPT") or load_prompt_from_file()
    return f"""
You are in a chat with human. (turn: {turn})

# Custom system prompt:
{custom}

Update your system prompt in every turn using the environment tool to set SYSTEM_PROMPT.
Your updated prompt should reflect what you learned from the conversation so far.
Do NOT repeat the wrapper text above — only set the inner custom prompt content.
    """

if PROMPT_FILE.exists():
    PROMPT_FILE.unlink()

turn = 0
print(f"\n{BOLD}{CYAN}{'=' * 50}")
print(f"  Autonomous Agent Chat")
print(f"{'=' * 50}{RESET}")
print(f"{DIM}  Type your message below. Press Ctrl+C to exit.{RESET}\n")

while True:
    turn += 1

    if PROMPT_FILE.exists():
        PROMPT_FILE.unlink()

    agent.system_prompt = construct_system_prompt(turn)
    save_prompt_to_file(agent.system_prompt)

    print(f"{DIM}{'─' * 50}{RESET}")
    user_input = input(f"{BOLD}{BLUE}  [Request #{turn}] ▶ {RESET}")

    if not user_input.strip():
        print(f"{DIM}  (empty input, skipped){RESET}")
        continue

    print(f"\n{BOLD}{GREEN}  [Response #{turn}]{RESET}")
    print(f"{DIM}  {'·' * 40}{RESET}")
    agent(user_input)

    custom_prompt = os.getenv("SYSTEM_PROMPT", "")
    if custom_prompt:
        save_prompt_to_file(custom_prompt)

    print()

