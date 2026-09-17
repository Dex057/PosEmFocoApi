FROM python:3.10-slim

WORKDIR /app

# Chromium + chromium-driver vêm do repositório padrão do Debian para amd64 E arm64
# (diferente do Google Chrome, que só publica pacote .deb para amd64) — assim a mesma
# imagem builda tanto numa máquina normal quanto num host ARM (ex.: Oracle Cloud Free Tier).
RUN apt-get update && \
    apt-get install -y --no-install-recommends chromium chromium-driver && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]