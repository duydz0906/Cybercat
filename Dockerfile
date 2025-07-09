FROM python:3.12-slim

# Cài ffmpeg và gói phụ thuộc
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc
WORKDIR /app

# Copy file yêu cầu
COPY requirements.txt .

# Cài Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn
COPY . .

# Chạy bot
CMD ["python", "main.py"]
