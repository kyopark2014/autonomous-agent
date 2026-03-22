"""
Interactive CLI for the Strands Research Agent.

Reads user input from the terminal, runs the agent, and prints the result.
Supports multi-turn conversation within a single session.
"""
import os
import sys
import json
import logging
import datetime
import socket
import re
from pathlib import Path

from strands import Agent
from strands_tools import shell, environment, use_agent, think
from strands_tools.utils.models.model import create_model
from strands_research_agent.tools import scraper
from strands_research_agent.handlers.callback_handler import callback_handler

from agent import construct_system_prompt, system_prompt

MEMORY_ID = os.getenv("BEDROCK_AGENTCORE_MEMORY_ID", "riv_research_agent_mem-r8gWdr5hjb")
REGION = os.getenv("AWS_REGION")
MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

os.environ.setdefault("STRANDS_MODEL_ID", MODEL_ID)
os.environ.setdefault("STRANDS_MAXS_TOKENS", "64000")
os.environ.setdefault(
    "STRANDS_ADDITIONAL_REQUEST_FIELDS",
    '{"anthropic_beta": ["interleaved-thinking-2025-05-14", "context-1m-2025-08-07"], "thinking": {"type": "enabled", "budget_tokens": 2048}}',
)

_SURROGATE_RE = re.compile(r'[\ud800-\udfff]')


def _sanitize_str(value):
    """Remove lone surrogate characters that break JSON/UTF-8 encoding."""
    if isinstance(value, str):
        return _SURROGATE_RE.sub('', value)
    return value


def _sanitize_input(text: str) -> str:
    """Sanitize user input: fix encoding issues, remove invalid characters."""
    text = text.encode('utf-8', errors='replace').decode('utf-8')
    text = _SURROGATE_RE.sub('', text)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text.strip()


def _sanitize_obj(obj):
    """Recursively sanitize all strings in a nested dict/list structure."""
    if isinstance(obj, str):
        return _sanitize_str(obj)
    if isinstance(obj, dict):
        return {k: _sanitize_obj(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_obj(item) for item in obj]
    return obj


def sanitize_messages(messages):
    """Clean surrogate characters from message history to prevent Bedrock JSON errors."""
    for i, msg in enumerate(messages):
        if isinstance(msg, dict):
            messages[i] = _sanitize_obj(msg)


def build_agent(user_input: str = "") -> Agent:
    tools = [system_prompt, shell, environment, use_agent, think, scraper]

    if MEMORY_ID and REGION:
        from bedrock_agentcore.memory.integrations.strands.config import (
            AgentCoreMemoryConfig,
            RetrievalConfig,
        )
        from bedrock_agentcore.memory.integrations.strands.session_manager import (
            AgentCoreMemorySessionManager,
        )
        from strands_tools.agent_core_memory import AgentCoreMemoryToolProvider

        actor_id = os.getenv("USER", "user")
        session_id = f"cli-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"

        memory_config = AgentCoreMemoryConfig(
            memory_id=MEMORY_ID,
            session_id=session_id,
            actor_id=actor_id,
            retrieval_config={
                f"/users/{actor_id}/facts": RetrievalConfig(top_k=3, relevance_score=0.5),
                f"/users/{actor_id}/preferences": RetrievalConfig(top_k=3, relevance_score=0.5),
            },
        )

        memory_provider = AgentCoreMemoryToolProvider(
            memory_id=MEMORY_ID,
            session_id=session_id,
            actor_id=actor_id,
            namespace="default",
            region=REGION,
        )

        tools += memory_provider.tools

        agent = Agent(
            model=create_model(provider=os.getenv("MODEL_PROVIDER", "bedrock")),
            session_manager=AgentCoreMemorySessionManager(memory_config, REGION),
            system_prompt=construct_system_prompt(user_input),
            tools=tools,
            load_tools_from_directory=True,
        )
    else:
        agent = Agent(
            model=create_model(provider=os.getenv("MODEL_PROVIDER", "bedrock")),
            system_prompt=construct_system_prompt(user_input),
            tools=tools,
            load_tools_from_directory=True,
        )

    return agent


def main():
    print("=== Strands Research Agent CLI ===")
    print("종료하려면 'exit' 또는 'quit'를 입력하세요.\n")

    agent = None

    while True:
        try:
            user_input = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n종료합니다.")
            break

        user_input = _sanitize_input(user_input)

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("종료합니다.")
            break

        if agent is None:
            agent = build_agent(user_input)

        try:
            if agent.messages:
                sanitize_messages(agent.messages)

                debug_path = Path("debug_messages.json")
                try:
                    sanitized = _sanitize_obj(agent.messages)
                    with open(debug_path, "w", encoding="utf-8") as f:
                        json.dump(sanitized, f, ensure_ascii=False, indent=2, default=str)
                    print(f"[DEBUG] 메시지 히스토리 저장: {debug_path} ({len(agent.messages)}개 메시지)")
                except Exception as dump_err:
                    print(f"[DEBUG] 메시지 덤프 실패: {dump_err}", file=sys.stderr)

                for i, msg in enumerate(agent.messages):
                    if isinstance(msg, dict) and msg.get("role") == "user":
                        for j, content in enumerate(msg.get("content", [])):
                            if isinstance(content, dict) and "toolResult" in content:
                                tr = content["toolResult"]
                                status = tr.get("status")
                                if status not in ("success", "error"):
                                    print(f"[DEBUG] ⚠ 잘못된 toolResult.status 발견! messages[{i}].content[{j}].toolResult.status = '{status}'")
                                tr_content = tr.get("content", [])
                                for k, c in enumerate(tr_content):
                                    if isinstance(c, dict):
                                        for key, val in c.items():
                                            if not isinstance(val, str):
                                                print(f"[DEBUG] ⚠ toolResult content 비정상 타입! messages[{i}].content[{j}].toolResult.content[{k}].{key} = {type(val).__name__}: {repr(val)[:200]}")

            result = agent(user_input)
            print(f"\nAgent> {result}\n")
        except Exception as e:
            print(f"\n[오류] {e}\n", file=sys.stderr)
            if agent and agent.messages:
                err_path = Path("debug_messages_error.json")
                try:
                    sanitized = _sanitize_obj(agent.messages)
                    with open(err_path, "w", encoding="utf-8") as f:
                        json.dump(sanitized, f, ensure_ascii=False, indent=2, default=str)
                    print(f"[DEBUG] 에러 시 메시지 히스토리 저장: {err_path} ({len(agent.messages)}개 메시지)", file=sys.stderr)
                except Exception as dump_err:
                    print(f"[DEBUG] 에러 시 메시지 덤프 실패: {dump_err}", file=sys.stderr)


if __name__ == "__main__":
    main()
