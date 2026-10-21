#!/bin/bash
# QuizletVN Server Runner dành cho macOS (MacBook / iMac)
# Nhấp đúp chuột vào file này để khởi chạy máy chủ!

cd "$(dirname "$0")"

clear
echo "=================================================================="
echo "      🚀 KHỞI ĐỘNG MÁY CHỦ QUIZLET VN TRÊN MACBOOK / MACOS"
echo "=================================================================="
echo ""

# 1. Kiểm tra python3 (Lệnh chuẩn trên macOS)
if command -v python3 &>/dev/null; then
    echo "[✔] Tìm thấy Python 3 trên MacBook!"
    echo "[*] Đang mở trình duyệt web..."
    sleep 1 && open "http://localhost:8000" &
    python3 server.py
    exit 0
fi

# 2. Kiểm tra node
if command -v node &>/dev/null; then
    echo "[✔] Tìm thấy Node.js trên MacBook!"
    echo "[*] Đang mở trình duyệt web..."
    sleep 1 && open "http://localhost:8000" &
    node server.js
    exit 0
fi

# 3. Kiểm tra python (nếu máy cũ có alias)
if command -v python &>/dev/null; then
    echo "[✔] Tìm thấy Python!"
    echo "[*] Đang mở trình duyệt web..."
    sleep 1 && open "http://localhost:8000" &
    python server.py
    exit 0
fi

# 4. Nếu chưa có: Hướng dẫn cài đặt Xcode Command Line Tools chỉ bằng 1 câu lệnh của Apple
echo "[!] MacBook của bạn chưa kích hoạt Python 3."
echo "👉 Đang yêu cầu macOS cài đặt công cụ chính thức từ Apple..."
xcode-select --install

echo ""
echo "Vui lòng bấm 'Cài đặt' (Install) ở cửa sổ vừa hiện lên."
echo "Sau khi cài xong (mất khoảng 1-2 phút), hãy nhấp đúp lại vào file này!"
read -p "Nhấn phím bất kỳ để đóng..."
