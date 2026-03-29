import logging
import sys
import json
import traceback
import boto3
import os

from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper

logging.basicConfig(
    level=logging.INFO,  # Default to INFO level
    format='%(filename)s:%(lineno)d | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("utils")

def load_config():
    config = None
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.json")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    return config

def get_contents_type(file_name):
    if file_name.lower().endswith((".jpg", ".jpeg")):
        content_type = "image/jpeg"
    elif file_name.lower().endswith((".pdf")):
        content_type = "application/pdf"
    elif file_name.lower().endswith((".txt")):
        content_type = "text/plain"
    elif file_name.lower().endswith((".csv")):
        content_type = "text/csv"
    elif file_name.lower().endswith((".ppt", ".pptx")):
        content_type = "application/vnd.ms-powerpoint"
    elif file_name.lower().endswith((".doc", ".docx")):
        content_type = "application/msword"
    elif file_name.lower().endswith((".xls")):
        content_type = "application/vnd.ms-excel"
    elif file_name.lower().endswith((".py")):
        content_type = "text/x-python"
    elif file_name.lower().endswith((".js")):
        content_type = "application/javascript"
    elif file_name.lower().endswith((".md")):
        content_type = "text/markdown"
    elif file_name.lower().endswith((".png")):
        content_type = "image/png"
    else:
        content_type = "no info"    
    return content_type

def get_s3_bucket(cfg: dict) -> str | None:
    """Return s3_bucket from config; if absent, discover it via AWS S3 API.

    Discovery searches for buckets whose name contains projectName.
    Result is kept in memory only — containers are ephemeral so writing
    back to config.json has no effect across restarts.
    """
    bucket = cfg.get("s3_bucket")
    if bucket:
        return bucket

    project_name = cfg.get("projectName", "").lower()
    region = cfg.get("region", "us-east-1")

    try:
        s3 = boto3.client("s3", region_name=region)
        all_buckets = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
        matched = [b for b in all_buckets if project_name in b] if project_name else all_buckets
        if matched:
            bucket = matched[0]
            logger.info(f"s3_bucket resolved from AWS: {bucket}")
    except Exception as e:
        logger.info(f"Failed to resolve s3_bucket: {e}")

    return bucket


def get_sharing_url(cfg: dict) -> str | None:
    """Return sharing_url from config; if absent, discover it via CloudFront API.

    Matches by s3_bucket origin domain when s3_bucket is set; falls back to
    the single enabled distribution if exactly one exists.
    Result is kept in memory only.
    """
    url = cfg.get("sharing_url")
    if url:
        return url

    s3_bucket = get_s3_bucket(cfg)
    region = cfg.get("region", "us-east-1")

    try:
        cf = boto3.client("cloudfront", region_name=region)
        distributions: list = []
        for page in cf.get_paginator("list_distributions").paginate():
            distributions.extend(page.get("DistributionList", {}).get("Items", []))

        enabled = [d for d in distributions if d.get("Enabled", True)]

        if s3_bucket:
            for dist in enabled:
                origins = dist.get("Origins", {}).get("Items", [])
                if any(s3_bucket in o.get("DomainName", "") for o in origins):
                    url = f"https://{dist['DomainName']}"
                    break

        if not url and len(enabled) == 1:
            url = f"https://{enabled[0]['DomainName']}"

        if url:
            logger.info(f"sharing_url resolved from CloudFront: {url}")
    except Exception as e:
        logger.info(f"Failed to resolve sharing_url: {e}")

    return url


config = load_config()

bedrock_region = config['region']
accountId = config['accountId']
projectName = config['projectName']
agent_runtime_role = config['agent_runtime_role']

aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
aws_session_token = os.environ.get('AWS_SESSION_TOKEN')

# api key to get information in agent
if aws_access_key and aws_secret_key:
    secretsmanager = boto3.client(
        service_name='secretsmanager',
        region_name=bedrock_region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        aws_session_token=aws_session_token,
    )
else:
    secretsmanager = boto3.client(
        service_name='secretsmanager',
        region_name=bedrock_region
    )
    
# api key to use Tavily Search
tavily_key = tavily_api_wrapper = ""
try:
    get_tavily_api_secret = secretsmanager.get_secret_value(
        SecretId=f"tavilyapikey-{projectName}"
    )
    #print('get_tavily_api_secret: ', get_tavily_api_secret)
    secret = json.loads(get_tavily_api_secret['SecretString'])
    #print('secret: ', secret)

    if "tavily_api_key" in secret:
        tavily_key = secret['tavily_api_key']
        #print('tavily_api_key: ', tavily_api_key)

        if tavily_key:
            tavily_api_wrapper = TavilySearchAPIWrapper(tavily_api_key=tavily_key)
            os.environ["TAVILY_API_KEY"] = tavily_key

        else:
            logger.info(f"tavily_key is required.")
except Exception as e: 
    logger.info(f"Tavily credential is required: {e}")
    # raise e
    pass

# api key to use Notion
notion_api_key = ""
try:
    get_notion_api_secret = secretsmanager.get_secret_value(
        SecretId=f"notionapikey-{projectName}"
    )
    secret = json.loads(get_notion_api_secret['SecretString'])

    if "notion_api_key" in secret:
        notion_api_key = secret['notion_api_key']

        if notion_api_key:
            os.environ["NOTION_API_KEY"] = notion_api_key
        else:
            logger.info(f"notion_api_key is required.")
except Exception as e:
    logger.info(f"Notion credential is required: {e}")
    pass




def load_mcp_env():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mcp_env_path = os.path.join(script_dir, "mcp.env")
    
    with open(mcp_env_path, "r", encoding="utf-8") as f:
        mcp_env = json.load(f)
    return mcp_env

def save_mcp_env(mcp_env):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mcp_env_path = os.path.join(script_dir, "mcp.env")
    
    with open(mcp_env_path, "w", encoding="utf-8") as f:
        json.dump(mcp_env, f)

