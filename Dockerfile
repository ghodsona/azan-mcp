FROM python:3.12-slim
WORKDIR /app
RUN pip install uv
COPY pyproject.toml README.md ./
RUN uv pip install --system .
COPY src/ ./src/
CMD ["python", "-m", "azan_mcp.server"]
