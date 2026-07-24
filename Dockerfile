FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV HF_HOME=/app/.cache/hf
ENV TORCH_HOME=/app/.cache/torch

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -m agent.worker download-files

RUN useradd -m appuser && chown -R appuser /app
USER appuser

CMD ["python", "-m", "agent.worker", "start"]
