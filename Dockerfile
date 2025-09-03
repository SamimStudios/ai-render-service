FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# FFmpeg + RAQM runtime deps (RTL/Arabic shaping)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libharfbuzz0b \
    libfribidi0 \
    libfreetype6 \
    libraqm0 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p out

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
