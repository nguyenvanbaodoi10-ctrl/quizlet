#!/usr/bin/env bash
cd "$(dirname "$0")"

echo "=================================================================="
echo "        🚀 KHỞI ĐỘNG MÁY CHỦ QUIZLET VN (MACOS / LINUX)"
echo "=================================================================="
echo ""

if command -v python3 &>/dev/null; then
    echo "[✔] Tìm thấy Python 3. Đang khởi chạy server.py..."
    python3 server.py
elif command -v node &>/dev/null; then
    echo "[✔] Tìm thấy Node.js. Đang khởi chạy server.js..."
    node server.js
elif command -v python &>/dev/null; then
    echo "[✔] Tìm thấy Python. Đang khởi chạy server.py..."
    python server.py
else
    echo "[X] Chưa tìm thấy Python hoặc Node.js trên máy tính của bạn."
    echo "    Vui lòng cài đặt Python (https://www.python.org) hoặc Node.js (https://nodejs.org)."
fi
