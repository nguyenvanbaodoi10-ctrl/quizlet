#!/usr/bin/env python3
"""
QuizletVN Server — Máy chủ quản lý Thẻ ghi nhớ & Bảng từ vựng học sinh
- Không yêu cầu cài thêm thư viện (chạy trực tiếp bằng Python 3 chuẩn: python3 server.py)
- Lưu trữ dữ liệu an toàn, tin cậy qua CSDL JSON (database/quizlet_data.json)
- Tự động phát hiện mạng nội bộ (Wi-Fi/LAN) để giáo viên chia sẻ link cho học sinh
"""

import os
import sys
import json
import socket
import threading
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

PORT = int(os.environ.get("PORT", 8000))
BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"
DB_DIR = BASE_DIR / "database"
DB_FILE = DB_DIR / "quizlet_data.json"

os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(PUBLIC_DIR, exist_ok=True)

db_lock = threading.Lock()

DEFAULT_DATA = {
    "folders": [
        {"id": "folder_ielts", "name": "IELTS & Học thuật", "desc": "Từ vựng học thuật C1-C2 & Reading/Writing", "icon": "🎓"},
        {"id": "folder_toeic", "name": "Công việc & TOEIC", "desc": "Tiếng Anh thương mại, văn phòng & giao tiếp", "icon": "💼"},
        {"id": "folder_tech", "name": "Công nghệ & Khoa học", "desc": "Thuật ngữ lập trình, AI & khoa học tự nhiên", "icon": "💻"},
        {"id": "folder_life", "name": "Chủ đề Đời sống & Xã hội", "desc": "Du lịch, môi trường, sức khỏe & văn hóa", "icon": "🌟"}
    ],
    "study_sets": [
        {
            "id": "set_ielts_english",
            "title": "IELTS Academic & Giao Tiếp Nâng Cao",
            "category": "IELTS & Học thuật",
            "description": "12 từ vựng C1/C2 quan trọng kèm phiên âm IPA chuẩn quốc tế và câu ví dụ thực tế.",
            "icon": "🎓",
            "best_match_time": None,
            "terms": [
                {"id": "t1", "term": "resilient", "ipa": "/rɪˈzɪl.jənt/", "pos": "ADJ", "definition": "Kiên cường — Có khả năng phục hồi nhanh chóng sau khó khăn, biến cố", "note": "Children are often very resilient.", "starred": True, "mastery": 2},
                {"id": "t2", "term": "ubiquitous", "ipa": "/juːˈbɪk.wɪ.təs/", "pos": "ADJ", "definition": "Phổ biến khắp nơi — Có mặt hoặc xuất hiện ở khắp mọi nơi cùng một lúc", "note": "Smartphones have become ubiquitous in modern life.", "starred": True, "mastery": 1},
                {"id": "t3", "term": "pragmatic", "ipa": "/præɡˈmæt.ɪk/", "pos": "ADJ", "definition": "Thực tế, thực dụng — Giải quyết vấn đề dựa trên tình hình thực tiễn thay vì lý thuyết suông", "note": "We need a pragmatic approach to this crisis.", "starred": False, "mastery": 2},
                {"id": "t4", "term": "mitigate", "ipa": "/ˈmɪt.ɪ.ɡeɪt/", "pos": "VERB", "definition": "Làm giảm nhẹ, xoa dịu — Làm giảm bớt mức độ nghiêm trọng hoặc tác động xấu của rủi ro", "note": "Planting trees helps mitigate climate change.", "starred": False, "mastery": 1},
                {"id": "t5", "term": "catalyst", "ipa": "/ˈkæt.əl.ɪst/", "pos": "NOUN", "definition": "Chất xúc tác — Nhân tố thúc đẩy một sự việc hoặc sự thay đổi diễn ra nhanh chóng hơn", "note": "Technology is a major catalyst for growth.", "starred": False, "mastery": 0},
                {"id": "t6", "term": "unprecedented", "ipa": "/ʌnˈpres.ɪ.den.tɪd/", "pos": "ADJ", "definition": "Chưa từng có tiền lệ — Chưa bao giờ xảy ra hoặc được biết đến trước đây", "note": "The heatwave reached unprecedented levels.", "starred": True, "mastery": 0},
                {"id": "t7", "term": "meticulous", "ipa": "/məˈtɪk.jə.ləs/", "pos": "ADJ", "definition": "Tỉ mỉ, kỹ lưỡng — Chú ý cẩn thận và chính xác đến từng chi tiết nhỏ nhất", "note": "She is meticulous about keeping accurate records.", "starred": False, "mastery": 0},
                {"id": "t8", "term": "sustainable", "ipa": "/səˈsteɪ.nə.bəl/", "pos": "ADJ", "definition": "Bền vững — Có thể duy trì lâu dài mà không làm cạn kiệt tài nguyên", "note": "Sustainable energy sources are vital.", "starred": False, "mastery": 2}
            ]
        },
        {
            "id": "set_lifelong_learning",
            "title": "Lifelong Learning & Education (Giáo dục & Học tập suốt đời)",
            "category": "IELTS & Học thuật",
            "description": "Bộ từ vựng chủ đề việc học suốt đời, phát triển bản thân và giáo dục hiện đại.",
            "icon": "📚",
            "best_match_time": None,
            "terms": [
                {"id": "l1", "term": "lifelong learning", "ipa": "/ˌlaɪf.lɒŋ ˈlɜː.nɪŋ/", "pos": "PHRASE", "definition": "Học tập suốt đời — Quá trình tự nguyện và chủ động theo đuổi tri thức trong suốt cuộc đời", "note": "Lifelong learning helps people adapt to a changing world.", "starred": True, "mastery": 2},
                {"id": "l2", "term": "curriculum", "ipa": "/kəˈrɪk.jə.ləm/", "pos": "NOUN", "definition": "Chương trình giảng dạy — Toàn bộ các môn học và nội dung đào tạo của nhà trường", "note": "Coding was added to the national curriculum.", "starred": False, "mastery": 1},
                {"id": "l3", "term": "literacy", "ipa": "/ˈlɪt.ər.ə.si/", "pos": "NOUN", "definition": "Trình độ biết đọc viết / Năng lực hiểu biết — Năng lực thành thạo một lĩnh vực", "note": "Digital literacy is essential for modern students.", "starred": False, "mastery": 0}
            ]
        },
        {
            "id": "set_work_toeic",
            "title": "Work, Career & TOEIC Business (Công việc & Sự nghiệp)",
            "category": "Công việc & TOEIC",
            "description": "Từ vựng tiếng Anh thương mại, phỏng vấn, hợp đồng và môi trường làm việc chuyên nghiệp.",
            "icon": "💼",
            "best_match_time": 15.2,
            "terms": [
                {"id": "b1", "term": "negotiation", "ipa": "/nəˌɡəʊ.ʃiˈeɪ.ʃən/", "pos": "NOUN", "definition": "Sự đàm phán, thương lượng — Quá trình thảo luận giữa các bên nhằm đi đến thỏa thuận chung", "note": "The contract is still under negotiation.", "starred": True, "mastery": 2},
                {"id": "b2", "term": "remuneration", "ipa": "/rɪˌmjuː.nərˈeɪ.ʃən/", "pos": "NOUN", "definition": "Tiền thù lao, đãi ngộ — Tổng mức lương thưởng và quyền lợi nhận được cho công việc", "note": "They offer a competitive remuneration package.", "starred": True, "mastery": 0},
                {"id": "b3", "term": "reimburse", "ipa": "/ˌriː.ɪmˈbɜːs/", "pos": "VERB", "definition": "Hoàn trả chi phí — Đền bù hoặc trả lại khoản tiền nhân viên đã chi tiêu trước cho công việc", "note": "The company will reimburse your travel expenses.", "starred": False, "mastery": 1}
            ]
        },
        {
            "id": "set_web_dev",
            "title": "Technology, AI & Software Engineering",
            "category": "Công nghệ & Khoa học",
            "description": "Thuật ngữ tiếng Anh chuyên ngành Công nghệ thông tin, Lập trình và Trí tuệ nhân tạo kèm IPA.",
            "icon": "💻",
            "best_match_time": 14.8,
            "terms": [
                {"id": "w1", "term": "algorithm", "ipa": "/ˈæl.ɡə.rɪ.ðəm/", "pos": "NOUN", "definition": "Thuật toán — Tập hợp hữu hạn các bước chỉ dẫn logic rõ ràng để giải quyết một bài toán", "note": "Search engines use complex algorithms.", "starred": True, "mastery": 2},
                {"id": "w2", "term": "authentication", "ipa": "/ɔːˌθen.tɪˈkeɪ.ʃən/", "pos": "NOUN", "definition": "Xác thực danh tính — Quá trình kiểm tra thông tin đăng nhập để xác nhận người dùng hợp lệ", "note": "Two-factor authentication protects user accounts.", "starred": True, "mastery": 1}
            ]
        },
        {
            "id": "set_environment_urban",
            "title": "Environment, Nature & Urbanization (Môi trường & Đô thị hóa)",
            "category": "Chủ đề Đời sống & Xã hội",
            "description": "Từ vựng trọng tâm về biến đổi khí hậu, đa dạng sinh học, thiên nhiên và phát triển đô thị.",
            "icon": "🌱",
            "best_match_time": None,
            "terms": [
                {"id": "s1", "term": "biodiversity", "ipa": "/ˌbaɪ.əʊ.daɪˈvɜː.sə.ti/", "pos": "NOUN", "definition": "Đa dạng sinh học — Sự phong phú của các loài sinh vật và hệ sinh thái trong tự nhiên", "note": "Rainforests support rich biodiversity.", "starred": True, "mastery": 1},
                {"id": "s2", "term": "urbanization", "ipa": "/ˌɜː.bən.aɪˈzeɪ.ʃən/", "pos": "NOUN", "definition": "Sự đô thị hóa — Quá trình mở rộng các thành phố và dịch chuyển dân cư từ nông thôn ra thành thị", "note": "Rapid urbanization creates housing pressure.", "starred": True, "mastery": 0}
            ]
        }
    ]
}

def read_db():
    with db_lock:
        if DB_FILE.exists():
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        write_db(DEFAULT_DATA)
        return json.loads(json.dumps(DEFAULT_DATA))

def write_db(data):
    with db_lock:
        temp_file = DB_DIR / "quizlet_data.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(temp_file, DB_FILE)

class QuizletServerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def _send_json(self, data, status_code=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length > 0:
                raw = self.rfile.read(length).decode("utf-8")
                return json.loads(raw)
        except Exception:
            pass
        return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. API: GET /api/folders
        if path == "/api/folders":
            db = read_db()
            self._send_json({"ok": True, "folders": db.get("folders", [])})
            return

        # 2. API: GET /api/sets
        if path == "/api/sets":
            db = read_db()
            sets = db.get("study_sets", [])
            category = query.get("category", [None])[0]
            search = (query.get("search", [""])[0] or "").lower()

            if category and category != "ALL":
                sets = [s for s in sets if s.get("category") == category]
            if search:
                sets = [
                    s for s in sets
                    if search in s.get("title", "").lower()
                    or search in s.get("description", "").lower()
                    or any(search in t.get("term", "").lower() or search in t.get("definition", "").lower() for t in s.get("terms", []))
                ]
            self._send_json({"ok": True, "sets": sets})
            return

        # 3. API: GET /api/sets/:id
        if path.startswith("/api/sets/"):
            set_id = path.replace("/api/sets/", "").strip("/")
            db = read_db()
            target = next((s for s in db.get("study_sets", []) if s.get("id") == set_id), None)
            if not target:
                self._send_json({"ok": False, "error": "Không tìm thấy học phần"}, 404)
                return
            self._send_json({"ok": True, "set": target})
            return

        # 4. API: GET /api/share/:folder_name
        if path.startswith("/api/share/"):
            raw_folder = path.replace("/api/share/", "").strip("/")
            folder_name = urllib.parse.unquote(raw_folder)
            db = read_db()
            folder = next((f for f in db.get("folders", []) if f.get("name") == folder_name or f.get("id") == folder_name), None)
            if not folder:
                folder = {"name": folder_name, "icon": "📁", "desc": "Thư mục học phần"}
            sets = [s for s in db.get("study_sets", []) if s.get("category") == folder.get("name")]
            total_words = sum(len(s.get("terms", [])) for s in sets)
            folder_dict = dict(folder)
            folder_dict["sets"] = sets
            folder_dict["total_words"] = total_words
            self._send_json({"ok": True, "folder": folder_dict})
            return

        # 5. Route trực tiếp: /share/:folder hoặc /notebook/:folder -> phục vụ student.html
        if path.startswith("/share/") or path.startswith("/notebook/"):
            student_file = PUBLIC_DIR / "student.html"
            if student_file.exists():
                content = student_file.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

        # 6. Static files
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        # 1. API: POST /api/folders
        if path == "/api/folders":
            name = (body.get("name") or "").strip()
            desc = (body.get("desc") or "").strip()
            icon = (body.get("icon") or "📁").strip()
            folder_id = body.get("id") or f"folder_{int(os.times()[4] * 1000)}"

            if not name:
                self._send_json({"ok": False, "error": "Tên thư mục không được để trống"}, 400)
                return

            db = read_db()
            existing = next((f for f in db.get("folders", []) if f.get("name", "").lower() == name.lower()), None)
            if existing:
                existing["desc"] = desc or existing.get("desc")
                existing["icon"] = icon or existing.get("icon")
            else:
                existing = {"id": folder_id, "name": name, "desc": desc or "Thư mục học phần", "icon": icon}
                db["folders"].append(existing)
            write_db(db)
            self._send_json({"ok": True, "folder": existing})
            return

        # 2. API: POST /api/sets
        if path == "/api/sets":
            title = (body.get("title") or "").strip()
            category = (body.get("category") or "IELTS & Học thuật").strip()
            description = (body.get("description") or "").strip()
            icon = (body.get("icon") or "📚").strip()
            terms = body.get("terms") or []
            set_id = body.get("id") or f"set_{int(os.times()[4] * 1000)}"

            if not title:
                self._send_json({"ok": False, "error": "Tiêu đề học phần không được để trống"}, 400)
                return

            db = read_db()
            if not any(f.get("name") == category for f in db.get("folders", [])):
                db["folders"].append({"id": f"folder_{int(os.times()[4] * 1000)}", "name": category, "desc": "Thư mục tự tạo", "icon": "📁"})

            new_set = {
                "id": set_id,
                "title": title,
                "category": category,
                "description": description,
                "icon": icon,
                "best_match_time": None,
                "terms": terms
            }
            db["study_sets"].insert(0, new_set)
            write_db(db)
            self._send_json({"ok": True, "id": set_id, "message": f"Đã lưu học phần '{title}' thành công!"})
            return

        self._send_json({"ok": False, "error": "Not Found"}, 404)

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        if path.startswith("/api/sets/"):
            set_id = path.replace("/api/sets/", "").strip("/")
            db = read_db()
            target = next((s for s in db.get("study_sets", []) if s.get("id") == set_id), None)
            if not target:
                self._send_json({"ok": False, "error": "Không tìm thấy học phần"}, 404)
                return
            target["title"] = body.get("title") or target["title"]
            target["category"] = body.get("category") or target["category"]
            target["description"] = body.get("description") or target["description"]
            if "terms" in body:
                target["terms"] = body["terms"]
            write_db(db)
            self._send_json({"ok": True, "message": "Đã cập nhật học phần thành công!"})
            return

        self._send_json({"ok": False, "error": "Not Found"}, 404)

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/folders/"):
            folder_name = urllib.parse.unquote(path.replace("/api/folders/", "").strip("/"))
            db = read_db()
            db["folders"] = [f for f in db.get("folders", []) if f.get("name") != folder_name and f.get("id") != folder_name]
            db["study_sets"] = [s for s in db.get("study_sets", []) if s.get("category") != folder_name]
            write_db(db)
            self._send_json({"ok": True, "message": f"Đã xoá thư mục '{folder_name}'!"})
            return

        if path.startswith("/api/sets/"):
            set_id = path.replace("/api/sets/", "").strip("/")
            db = read_db()
            db["study_sets"] = [s for s in db.get("study_sets", []) if s.get("id") != set_id]
            write_db(db)
            self._send_json({"ok": True, "message": "Đã xoá học phần thành công!"})
            return

        self._send_json({"ok": False, "error": "Not Found"}, 404)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def run_server():
    read_db() # Khởi tạo dữ liệu
    local_ip = get_local_ip()
    server_address = ("0.0.0.0", PORT)
    httpd = HTTPServer(server_address, QuizletServerHandler)

    print("=" * 66)
    print("🚀 QUIZLET VN SERVER ĐANG HOẠT ĐỘNG THÀNH CÔNG!")
    print("=" * 66)
    print(f"👉 Truy cập cục bộ (Máy này):   http://localhost:{PORT}")
    print(f"👉 Truy cập qua mạng LAN/Wi-Fi: http://{local_ip}:{PORT}")
    print(f"👉 Link học sinh chép từ mẫu:   http://{local_ip}:{PORT}/share/IELTS%20%26%20H%E1%BB%8Dc%20thu%E1%BA%ADt")
    print(f"📁 CSDL JSON lưu tại:           {DB_FILE}")
    print("=" * 66)
    print("Nhấn Ctrl + C để dừng máy chủ.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng máy chủ an toàn.")
        sys.exit(0)

if __name__ == "__main__":
    run_server()
