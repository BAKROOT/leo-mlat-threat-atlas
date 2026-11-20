# Reproduce every result of the repository:  docker build -t leo-mlat . && docker run --rm leo-mlat
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends make && rm -rf /var/lib/apt/lists/*
WORKDIR /repo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["sh", "-c", "make check && make panel && make test && make simulate"]
