FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Supaya log lebih jelas & tidak buffering
ENV PYTHONUNBUFFERED=1

# Install dependency system (opsional tapi bagus untuk beberapa library bot)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements dulu (biar caching lebih optimal)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua source code
COPY . .

# Jalankan bot
CMD ["python", "bot.py"]
