"""
This module implements a conversation agent with the ability to dynamically
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
from strands_tools import shell, environment, use_agent, think, swarm, graph, journal
from strands_tools.utils.models.model import create_model

agent = Agent(tools=[shell, environment, use_agent, think, swarm, graph, journal], load_tools_from_directory=True)

while True:
    agent(input("\n~ "))
