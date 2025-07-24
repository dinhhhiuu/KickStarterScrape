# Dùng image nhẹ có Python
FROM python:3.10-slim

# Cập nhật và cài Chromium + các phụ thuộc
RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libxss1 \
    libasound2 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Đặt biến môi trường để trỏ đúng tới chromium binary
ENV CHROME_BINARY=/usr/bin/chromium

# Tạo thư mục và copy code vào container
WORKDIR /app
COPY . /app

# Expose port
EXPOSE 10000

# Cài Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Chạy Flask app
CMD ["python", "app.py"]
