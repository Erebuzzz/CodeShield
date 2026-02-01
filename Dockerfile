FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY src/ src/
COPY README.md .

# Install dependencies and the package
RUN pip install --no-cache-dir .

# Expose port if needed (MCP usually uses stdio or SSE on a port)
# LeanMCP might expect an HTTP server for SSE.
# The FastMCP server by default uses stdio, but can run SSE.
# We'll explicitly run it.
# Note: server.py main block invokes run() which does stdio.
# We might need to adjust for SSE if deploying as a service.

# Env var for unbuffered output
ENV PYTHONUNBUFFERED=1

# Default command: Standard MCP (Stdio)
CMD ["python", "-m", "codeshield.mcp.server"]
