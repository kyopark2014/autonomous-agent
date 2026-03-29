import logging
import sys
import os
import boto3
import utils

logging.basicConfig(
    level=logging.INFO,  # Default to INFO level
    format='%(filename)s:%(lineno)d | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("mcp-config")

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")

config = utils.load_config()
logger.info(f"config: {config}")
region = config["region"] if "region" in config else "us-west-2"
projectName = config["projectName"] if "projectName" in config else "mcp"

workingDir = os.path.dirname(os.path.abspath(__file__))
logger.info(f"workingDir: {workingDir}")

mcp_user_config = {}    

def get_agent_runtime_arn(mcp_type: str):
    #logger.info(f"mcp_type: {mcp_type}")
    agent_runtime_name = f"{projectName.lower().replace('-', '_')}_{mcp_type.replace('-', '_')}"
    logger.info(f"agent_runtime_name: {agent_runtime_name}")
    client = boto3.client('bedrock-agentcore-control', region_name=region)
    response = client.list_agent_runtimes(
        maxResults=100
    )
    logger.info(f"response: {response}")
    
    agentRuntimes = response['agentRuntimes']
    for agentRuntime in agentRuntimes:
        if agentRuntime["agentRuntimeName"] == agent_runtime_name:
            logger.info(f"agent_runtime_name: {agent_runtime_name}, agentRuntimeArn: {agentRuntime["agentRuntimeArn"]}")
            return agentRuntime["agentRuntimeArn"]
    return None

def load_config(mcp_type):
    global bearer_token, gateway_url

    if mcp_type == "aws document":
        mcp_type = 'aws_documentation'

    if mcp_type == "tavily":
        return {
            "mcpServers": {
                "tavily-search": {
                    "command": "python",
                    "args": [
                        f"{workingDir}/mcp_server_tavily.py"
                    ]
                }
            }
        }
    
    elif mcp_type == "aws_documentation":
        return {
            "mcpServers": {
                "awslabs.aws-documentation-mcp-server": {
                    "command": "uvx",
                    "args": ["awslabs.aws-documentation-mcp-server@latest"],
                    "env": {
                        "FASTMCP_LOG_LEVEL": "ERROR"
                    }
                }
            }
        }
    
    elif mcp_type == "web_fetch":
        return {
            "mcpServers": {
                "web_fetch": {
                    "command": "npx",
                    "args": ["-y", "mcp-server-fetch-typescript"]
                }
            }
        }
    
    elif mcp_type == "korea_weather":
        return {
            "mcpServers": {
                "korea-weather": {
                    "command": "python",
                    "args": [f"{workingDir}/mcp_server_korea_weather.py"]
                }
            }
        }
    
    elif mcp_type == "notion":
        return {
            "mcpServers": {
                "notionApi": {
                    "command": "npx",
                    "args": ["-y", "@notionhq/notion-mcp-server"],
                    "env": {
                        "NOTION_TOKEN": utils.notion_api_key
                    }
                }
            }
        }    
        
    elif mcp_type == "사용자 설정":
        return mcp_user_config
    
    else:
        return {"mcpServers": {}}

def load_selected_config(mcp_servers: dict):
    logger.info(f"mcp_servers: {mcp_servers}")
    
    loaded_config = {}
    for server in mcp_servers:
        config = load_config(server)        
        if config:
            loaded_config.update(config["mcpServers"])
    return {
        "mcpServers": loaded_config
    }
