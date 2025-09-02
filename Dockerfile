FROM python:3.11-slim

# Install FFmpeg and libraqm dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    librsvg2-bin \
    libraqm \
    libfribidi0 \
    libharfbuzz0b \
    libfreetype6 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p out

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
