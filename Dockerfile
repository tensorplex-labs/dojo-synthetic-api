FROM python:3.11-slim-buster as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc curl

COPY pyproject.toml ./

RUN pip install --upgrade pip && \
    pip install --user .

FROM python:3.11-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y curl docker.io && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

COPY . .

EXPOSE 5003

CMD ["python", "main.py"]
