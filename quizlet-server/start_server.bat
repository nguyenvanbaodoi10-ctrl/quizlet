@echo off
chcp 65001 >nul
title QuizletVN Server Runner
cls

echo ==================================================================
echo         🚀 KHỞI ĐỘNG MÁY CHỦ QUIZLET VN (TỰ ĐỘNG)
echo ==================================================================
echo.

:: 1. Kiểm tra Python
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [✔] Tìm thấy Python trên máy tính. Đang khởi chạy server.py...
    echo.
    python server.py
    goto end
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [✔] Tìm thấy Python Launcher (py). Đang khởi chạy server.py...
    echo.
    py server.py
    goto end
)

:: 2. Kiểm tra Node.js
where node >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [✔] Tìm thấy Node.js trên máy tính. Đang khởi chạy server.js...
    echo.
    node server.js
    goto end
)

:: 3. Nếu không có cả Python lẫn Node.js -> Dùng PowerShell có sẵn trong Windows (Zero-install)
echo [i] Máy tính chưa cài Python hoặc Node.js.
echo [✔] Đang tự động chạy máy chủ bằng Windows PowerShell tích hợp sẵn...
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0server.ps1"

:end
pause
