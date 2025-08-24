FROM python:3.11-slim

# 1) Install ffmpeg for encoding
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*

# 2) App files
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code + fonts + keep output folder
COPY . .
RUN mkdir -p out

# 3) Expose and run
ENV PORT=8000
EXPOSE 8000
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]
