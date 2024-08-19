FROM python:3.11-slim-buster as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc curl

COPY requirements.txt ./

RUN pip install --upgrade pip && \
    pip install --user -r requirements.txt

FROM python:3.11-slim-buster

WORKDIR /app

RUN apt-get update && apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

COPY . .

EXPOSE 5003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5003", "--workers", "4"]
