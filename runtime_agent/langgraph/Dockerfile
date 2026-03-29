FROM --platform=linux/arm64 python:3.13-slim

WORKDIR /app

# Install Node.js and npm (for npx)
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install MCP packages globally
RUN npm install -g @modelcontextprotocol/server-filesystem

# Install mcp-server-fetch-typescript and Playwright browsers
RUN npx -y mcp-server-fetch-typescript --version 2>/dev/null || true && \
    npx playwright install --with-deps chromium

# PPT npm packages (global + local so require() works from any directory, including /tmp)
RUN npm install -g pptxgenjs sharp react react-dom react-icons && \
    mkdir -p /app/node_modules && \
    npm install --prefix /app pptxgenjs sharp react react-dom react-icons

# Allow require('pptxgenjs') to resolve from any working directory
ENV NODE_PATH=/usr/local/lib/node_modules:/app/node_modules

# System packages: poppler-utils (pdftoppm), LibreOffice (soffice), cairosvg deps, Korean fonts
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libreoffice \
    libcairo2-dev \
    libffi-dev \
    fonts-nanum \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# skill: execute_code / myslide - PPTX creation and editing
RUN pip install python-pptx
# skill: myslide - background image generation, SVG to PNG conversion, PPTX text extraction
RUN pip install Pillow cairosvg "markitdown[pptx]"
# skill: pdf - PDF creation, reading, merging, and table extraction
RUN pip install reportlab pypdf pdfplumber
# skill: xlsx - Excel data analysis, creation, and formula editing
RUN pip install pandas openpyxl
# skill.py - SKILL.md frontmatter parsing
RUN pip install PyYAML
RUN pip install pytz
RUN pip install bedrock-agentcore uv

# OpenTelemetry
RUN pip install aws-opentelemetry-distro>=0.10.0

RUN pip install boto3 botocore --upgrade
RUN pip install langchain_aws langchain langchain_community langchain_experimental langgraph
RUN pip install mcp langchain-mcp-adapters
RUN pip install tavily-python python-dotenv

COPY . .

# Add the current directory to Python path
ENV PYTHONPATH=/app

EXPOSE 8080

CMD ["uv", "run", "opentelemetry-instrument", "uvicorn", "agent:app", "--host", "0.0.0.0", "--port", "8080"]