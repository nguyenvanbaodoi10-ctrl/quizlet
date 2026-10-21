# QuizletVN Server Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Sao chép toàn bộ mã nguồn máy chủ và thư mục web
COPY . /app

# Mở cổng 8000
EXPOSE 8000

ENV PORT=8000

# Khởi chạy máy chủ Python chuẩn (không cần thêm thư viện ngoài)
CMD ["python3", "server.py"]
