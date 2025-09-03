FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Runtime deps only (ffmpeg + fonts); no dev headers needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libfreetype6 \
    fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
 && pip install -r requirements.txt

COPY . .
RUN mkdir -p out

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
