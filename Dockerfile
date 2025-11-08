FROM python:3.14-slim

ARG OPENAI_API_KEY
ENV OPENAI_API_KEY=$OPENAI_API_KEY

WORKDIR /opt/ml

COPY . .


RUN pip install uv && uv sync

EXPOSE 8000

ENTRYPOINT ["uv", "run", "uvicorn", "app.views:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--limit-concurrency", "2000", "--timeout-keep-alive", "10"]