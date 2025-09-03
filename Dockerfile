FROM python:3.11-slim

# Install FFmpeg and RAQM runtime deps (for proper Arabic shaping)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libharfbuzz0b \
    libfribidi0 \
    libfreetype6 \
    libraqm0 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p out

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
