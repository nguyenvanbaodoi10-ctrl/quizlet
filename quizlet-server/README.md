# 🚀 QuizletVN Server — Hướng Dẫn Vận Hành Máy Chủ

Dự án này giúp bạn biến ứng dụng **QuizletVN** thành một **máy chủ lưu trữ tập trung**, hỗ trợ học sinh mở đường link chép từ vựng trước khi đến lớp từ mọi thiết bị (điện thoại, máy tính bảng, máy tính) mà **không cần cài đặt phức tạp**.

---

## ⚡ CÁCH 1: NHẤP ĐÚP CHUỘT LÀ CHẠY NGAY (DÀNH CHO WINDOWS — KHÔNG CẦN CÀI PYTHON)

Nếu bạn dùng hệ điều hành Windows (Windows 10, 11, 7, 8):
1. Giải nén thư mục `quizlet-server`.
2. **Nhấp đúp chuột vào tệp `start_server.bat`**.
3. Tệp này sẽ tự động nhận diện:
   * Nếu máy có Python -> Tự chạy bằng Python.
   * Nếu máy có Node.js -> Tự chạy bằng Node.js.
   * **Nếu máy CHƯA CÀI GÌ CẢ** -> Tự động dùng công cụ **PowerShell có sẵn 100% trong Windows** để khởi động máy chủ và tự mở trình duyệt `http://localhost:8000`! Bạn hoàn toàn **không cần tải hay cài đặt thêm bất kỳ phần mềm nào**!

---

## 🌐 CÁCH 2: ĐƯA LÊN MẠNG INTERNET ONLINE MIỄN PHÍ 24/7 (KHÔNG CẦN BẬT MÁY TÍNH)

Nếu bạn muốn học sinh ở nhà hoặc bất kỳ đâu cũng mở được link mà không cần máy tính của bạn phải luôn bật:

### Lựa chọn A: Render.com (Miễn phí 100% — Khuyên dùng)
1. Đăng ký tài khoản miễn phí tại [Render.com](https://render.com).
2. Chọn **New Web Service** và tải mã nguồn thư mục này lên (hoặc kết nối qua GitHub).
3. Cấu hình nhanh:
   * **Environment**: `Python 3`
   * **Start Command**: `python3 server.py`
4. Bấm **Create Web Service**. Sau 1 phút, bạn sẽ có đường link cố định công khai:
   `https://quizlet-vn-cua-ban.onrender.com`
5. Gửi đường link cho học sinh:
   `https://quizlet-vn-cua-ban.onrender.com/share/IELTS%20%26%20H%E1%BB%8Dc%20thu%E1%BA%ADt`

### Lựa chọn B: Vercel / Netlify (Dành cho web tĩnh)
Bạn chỉ cần kéo thả toàn bộ thư mục `public` lên [Vercel.com](https://vercel.com) hoặc [Netlify.com](https://netlify.com) là có ngay trang web hoạt động online tức thì.

---

## 🟢 CÁCH 3: CHẠY BẰNG NODE.JS (NẾU MÁY BẠN CÓ NODE.JS)

Mở Terminal / Command Prompt trong thư mục `quizlet-server` và gõ:
```bash
node server.js
```
Máy chủ Node.js sẽ khởi động ngay lập tức mà không cần cài đặt thêm thư viện (`npm install`).

---

## 🐍 CÁCH 4: NẾU BẠN VẪN MUỐN CÀI PYTHON CHUẨN

Lý do phổ biến nhất khiến bạn không chạy được lệnh `python` trên Windows là do lúc cài đặt chưa tích chọn thêm Python vào hệ thống:
1. Tải bản cài đặt Python chính thức từ: [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. **Quan trọng nhất:** Khi bảng cài đặt hiện lên, **hãy tích vào ô tròn ở dưới cùng: `☑ Add python.exe to PATH`**.
3. Bấm **Install Now**.
4. Sau khi cài xong, mở lại cửa sổ Terminal mới và gõ lệnh:
   ```bash
   python server.py
   ```
   (Máy chủ dùng thư viện có sẵn của Python nên **không cần chạy `pip install`** bất cứ thứ gì).

---

## 📡 Danh Sách Các Đường Dẫn API & Giao Diện

| Đường dẫn | Chức năng |
| :--- | :--- |
| `http://localhost:8000/` | Mở giao diện chính QuizletVN đầy đủ tính năng |
| `http://<IP-máy-chủ>:8000/share/:tên_thư_mục` | Đường link sạch cho học sinh mở bảng chép từ vựng |
| `http://localhost:8000/api/folders` | Lấy danh sách thư mục lưu trữ |
| `http://localhost:8000/api/sets` | Lấy danh sách học phần và từ vựng |
| `http://localhost:8000/api/share/:tên_thư_mục` | Trả về JSON từ vựng theo thư mục |
