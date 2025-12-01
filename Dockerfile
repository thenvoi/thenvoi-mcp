FROM python:3.12-slim

WORKDIR /app

# Install uv and create venv
RUN pip install uv && python -m venv .venv

# Install all dependencies from PyPI first
RUN .venv/bin/pip install pydantic pydantic-core pydantic-settings mcp uvicorn httpx anyio starlette sse-starlette

# Copy only the private thenvoi_api SDK (pure Python, not on PyPI)
COPY .venv/lib/python3.14/site-packages/thenvoi_api/ .venv/lib/python3.12/site-packages/thenvoi_api/

# Copy project source
COPY src/ ./src/

# SSE transport configuration
ENV MCP_TRANSPORT=sse
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

EXPOSE 8000

ENV PYTHONPATH=/app/src
CMD [".venv/bin/python", "-m", "thenvoi_mcp.server"]
