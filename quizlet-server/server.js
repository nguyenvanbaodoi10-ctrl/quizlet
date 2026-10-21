const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');
const os = require('os');

const PORT = process.env.PORT || 8000;
const PUBLIC_DIR = path.join(__dirname, 'public');
const DB_FILE = path.join(__dirname, 'database', 'quizlet_data.json');

// Đảm bảo thư mục tồn tại
if (!fs.existsSync(path.join(__dirname, 'database'))) {
  fs.mkdirSync(path.join(__dirname, 'database'), { recursive: true });
}
if (!fs.existsSync(PUBLIC_DIR)) {
  fs.mkdirSync(PUBLIC_DIR, { recursive: true });
}

// Cấu trúc dữ liệu ban đầu
const DEFAULT_DATA = {
  folders: [
    { id: 'folder_ielts', name: 'IELTS & Học thuật', desc: 'Từ vựng học thuật C1-C2 & Reading/Writing', icon: '🎓' },
    { id: 'folder_toeic', name: 'Công việc & TOEIC', desc: 'Tiếng Anh thương mại, văn phòng & giao tiếp', icon: '💼' },
    { id: 'folder_tech', name: 'Công nghệ & Khoa học', desc: 'Thuật ngữ lập trình, AI & khoa học tự nhiên', icon: '💻' },
    { id: 'folder_life', name: 'Chủ đề Đời sống & Xã hội', desc: 'Du lịch, môi trường, sức khỏe & văn hóa', icon: '🌟' }
  ],
  study_sets: [
    {
      id: 'set_ielts_english',
      title: 'IELTS Academic & Giao Tiếp Nâng Cao',
      category: 'IELTS & Học thuật',
      description: '12 từ vựng C1/C2 quan trọng kèm phiên âm IPA chuẩn quốc tế và câu ví dụ thực tế.',
      icon: '🎓',
      best_match_time: null,
      terms: [
        { id: 't1', term: 'resilient', ipa: '/rɪˈzɪl.jənt/', pos: 'ADJ', definition: 'Kiên cường — Có khả năng phục hồi nhanh chóng sau khó khăn, biến cố', note: 'Children are often very resilient.', starred: true, mastery: 2 },
        { id: 't2', term: 'ubiquitous', ipa: '/juːˈbɪk.wɪ.təs/', pos: 'ADJ', definition: 'Phổ biến khắp nơi — Có mặt hoặc xuất hiện ở khắp mọi nơi cùng một lúc', note: 'Smartphones have become ubiquitous in modern life.', starred: true, mastery: 1 },
        { id: 't3', term: 'pragmatic', ipa: '/præɡˈmæt.ɪk/', pos: 'ADJ', definition: 'Thực tế, thực dụng — Giải quyết vấn đề dựa trên tình hình thực tiễn thay vì lý thuyết suông', note: 'We need a pragmatic approach to this crisis.', starred: false, mastery: 2 },
        { id: 't4', term: 'mitigate', ipa: '/ˈmɪt.ɪ.ɡeɪt/', pos: 'VERB', definition: 'Làm giảm nhẹ, xoa dịu — Làm giảm bớt mức độ nghiêm trọng hoặc tác động xấu của rủi ro', note: 'Planting trees helps mitigate climate change.', starred: false, mastery: 1 },
        { id: 't5', term: 'catalyst', ipa: '/ˈkæt.əl.ɪst/', pos: 'NOUN', definition: 'Chất xúc tác — Nhân tố thúc đẩy một sự việc hoặc sự thay đổi diễn ra nhanh chóng hơn', note: 'Technology is a major catalyst for growth.', starred: false, mastery: 0 },
        { id: 't6', term: 'unprecedented', ipa: '/ʌnˈpres.ɪ.den.tɪd/', pos: 'ADJ', definition: 'Chưa từng có tiền lệ — Chưa bao giờ xảy ra hoặc được biết đến trước đây', note: 'The heatwave reached unprecedented levels.', starred: true, mastery: 0 },
        { id: 't7', term: 'meticulous', ipa: '/məˈtɪk.jə.ləs/', pos: 'ADJ', definition: 'Tỉ mỉ, kỹ lưỡng — Chú ý cẩn thận và chính xác đến từng chi tiết nhỏ nhất', note: 'She is meticulous about keeping accurate records.', starred: false, mastery: 0 },
        { id: 't8', term: 'sustainable', ipa: '/səˈsteɪ.nə.bəl/', pos: 'ADJ', definition: 'Bền vững — Có thể duy trì lâu dài mà không làm cạn kiệt tài nguyên', note: 'Sustainable energy sources are vital.', starred: false, mastery: 2 }
      ]
    },
    {
      id: 'set_lifelong_learning',
      title: 'Lifelong Learning & Education (Giáo dục & Học tập suốt đời)',
      category: 'IELTS & Học thuật',
      description: 'Bộ từ vựng chủ đề việc học suốt đời, phát triển bản thân và giáo dục hiện đại.',
      icon: '📚',
      best_match_time: null,
      terms: [
        { id: 'l1', term: 'lifelong learning', ipa: '/ˌlaɪf.lɒŋ ˈlɜː.nɪŋ/', pos: 'PHRASE', definition: 'Học tập suốt đời — Quá trình tự nguyện và chủ động theo đuổi tri thức trong suốt cuộc đời', note: 'Lifelong learning helps people adapt to a changing world.', starred: true, mastery: 2 },
        { id: 'l2', term: 'curriculum', ipa: '/kəˈrɪk.jə.ləm/', pos: 'NOUN', definition: 'Chương trình giảng dạy — Toàn bộ các môn học và nội dung đào tạo của nhà trường', note: 'Coding was added to the national curriculum.', starred: false, mastery: 1 },
        { id: 'l3', term: 'literacy', ipa: '/ˈlɪt.ər.ə.si/', pos: 'NOUN', definition: 'Trình độ biết đọc viết / Năng lực hiểu biết — Năng lực thành thạo một lĩnh vực', note: 'Digital literacy is essential for modern students.', starred: false, mastery: 0 }
      ]
    },
    {
      id: 'set_work_toeic',
      title: 'Work, Career & TOEIC Business (Công việc & Sự nghiệp)',
      category: 'Công việc & TOEIC',
      description: 'Từ vựng tiếng Anh thương mại, phỏng vấn, hợp đồng và môi trường làm việc chuyên nghiệp.',
      icon: '💼',
      best_match_time: 15.2,
      terms: [
        { id: 'b1', term: 'negotiation', ipa: '/nəˌɡəʊ.ʃiˈeɪ.ʃən/', pos: 'NOUN', definition: 'Sự đàm phán, thương lượng — Quá trình thảo luận giữa các bên nhằm đi đến thỏa thuận chung', note: 'The contract is still under negotiation.', starred: true, mastery: 2 },
        { id: 'b2', term: 'remuneration', ipa: '/rɪˌmjuː.nərˈeɪ.ʃən/', pos: 'NOUN', definition: 'Tiền thù lao, đãi ngộ — Tổng mức lương thưởng và quyền lợi nhận được cho công việc', note: 'They offer a competitive remuneration package.', starred: true, mastery: 0 },
        { id: 'b3', term: 'reimburse', ipa: '/ˌriː.ɪmˈbɜːs/', pos: 'VERB', definition: 'Hoàn trả chi phí — Đền bù hoặc trả lại khoản tiền nhân viên đã chi tiêu trước cho công việc', note: 'The company will reimburse your travel expenses.', starred: false, mastery: 1 }
      ]
    }
  ]
};

function readDb() {
  try {
    if (fs.existsSync(DB_FILE)) {
      const raw = fs.readFileSync(DB_FILE, 'utf8');
      return JSON.parse(raw);
    }
  } catch (e) {}
  writeDb(DEFAULT_DATA);
  return DEFAULT_DATA;
}

function writeDb(data) {
  try {
    fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2), 'utf8');
  } catch (e) {
    console.error('Lỗi ghi CSDL:', e);
  }
}

function sendJson(res, data, status = 200) {
  const body = Buffer.from(JSON.stringify(data, null, 2), 'utf8');
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': body.length,
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
  });
  res.end(body);
}

function getLocalIp() {
  const nets = os.networkInterfaces();
  for (const name of Object.keys(nets)) {
    for (const net of nets[name]) {
      if (net.family === 'IPv4' && !net.internal) {
        return net.address;
      }
    }
  }
  return '127.0.0.1';
}

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml'
};

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const method = req.method.toUpperCase();

  // Handle CORS Preflight
  if (method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    });
    res.end();
    return;
  }

  // Parse JSON Body for POST/PUT
  let bodyBuffer = [];
  req.on('data', chunk => bodyBuffer.push(chunk));
  req.on('end', () => {
    let body = {};
    if (bodyBuffer.length > 0) {
      try {
        body = JSON.parse(Buffer.concat(bodyBuffer).toString('utf8'));
      } catch (e) {}
    }

    // 1. API: GET /api/folders
    if (method === 'GET' && pathname === '/api/folders') {
      const db = readDb();
      return sendJson(res, { ok: true, folders: db.folders });
    }

    // 2. API: POST /api/folders
    if (method === 'POST' && pathname === '/api/folders') {
      const db = readDb();
      const name = (body.name || '').trim();
      if (!name) return sendJson(res, { ok: false, error: 'Tên thư mục không được để trống' }, 400);

      let existing = db.folders.find(f => f.name.toLowerCase() === name.toLowerCase());
      if (existing) {
        existing.desc = body.desc || existing.desc;
        existing.icon = body.icon || existing.icon;
      } else {
        existing = {
          id: body.id || `folder_${Date.now()}`,
          name,
          desc: body.desc || 'Thư mục học phần',
          icon: body.icon || '📁'
        };
        db.folders.push(existing);
      }
      writeDb(db);
      return sendJson(res, { ok: true, folder: existing });
    }

    // 3. API: DELETE /api/folders/:name
    if (method === 'DELETE' && pathname.startsWith('/api/folders/')) {
      const folderName = decodeURIComponent(pathname.replace('/api/folders/', '').trim());
      const db = readDb();
      db.folders = db.folders.filter(f => f.name !== folderName && f.id !== folderName);
      db.study_sets = db.study_sets.filter(s => s.category !== folderName);
      writeDb(db);
      return sendJson(res, { ok: true, message: `Đã xoá thư mục "${folderName}"` });
    }

    // 4. API: GET /api/sets
    if (method === 'GET' && pathname === '/api/sets') {
      const db = readDb();
      let sets = db.study_sets || [];
      const cat = parsedUrl.query.category;
      const search = (parsedUrl.query.search || '').toLowerCase();
      if (cat && cat !== 'ALL') {
        sets = sets.filter(s => s.category === cat);
      }
      if (search) {
        sets = sets.filter(s =>
          s.title.toLowerCase().includes(search) ||
          (s.description || '').toLowerCase().includes(search) ||
          (s.terms || []).some(t => t.term.toLowerCase().includes(search) || t.definition.toLowerCase().includes(search))
        );
      }
      return sendJson(res, { ok: true, sets });
    }

    // 5. API: POST /api/sets
    if (method === 'POST' && pathname === '/api/sets') {
      const db = readDb();
      const title = (body.title || '').trim();
      if (!title) return sendJson(res, { ok: false, error: 'Tiêu đề không được để trống' }, 400);
      const newSet = {
        id: body.id || `set_${Date.now()}`,
        title,
        category: body.category || 'IELTS & Học thuật',
        description: body.description || '',
        icon: body.icon || '📚',
        best_match_time: null,
        terms: body.terms || []
      };
      db.study_sets.unshift(newSet);
      writeDb(db);
      return sendJson(res, { ok: true, id: newSet.id, message: 'Đã lưu học phần thành công!' });
    }

    // 6. API: PUT /api/sets/:id
    if (method === 'PUT' && pathname.startsWith('/api/sets/')) {
      const setId = pathname.replace('/api/sets/', '').trim();
      const db = readDb();
      const target = db.study_sets.find(s => s.id === setId);
      if (!target) return sendJson(res, { ok: false, error: 'Không tìm thấy học phần' }, 404);
      target.title = body.title || target.title;
      target.category = body.category || target.category;
      target.description = body.description || target.description;
      if (body.terms) target.terms = body.terms;
      writeDb(db);
      return sendJson(res, { ok: true, message: 'Đã cập nhật học phần thành công!' });
    }

    // 7. API: DELETE /api/sets/:id
    if (method === 'DELETE' && pathname.startsWith('/api/sets/')) {
      const setId = pathname.replace('/api/sets/', '').trim();
      const db = readDb();
      db.study_sets = db.study_sets.filter(s => s.id !== setId);
      writeDb(db);
      return sendJson(res, { ok: true, message: 'Đã xoá học phần thành công!' });
    }

    // 8. API: GET /api/share/:folderName
    if (method === 'GET' && pathname.startsWith('/api/share/')) {
      const folderName = decodeURIComponent(pathname.replace('/api/share/', '').trim());
      const db = readDb();
      const folder = db.folders.find(f => f.name === folderName || f.id === folderName) || { name: folderName, icon: '📁', desc: '' };
      const sets = db.study_sets.filter(s => s.category === folder.name);
      let total_words = 0;
      sets.forEach(s => { total_words += (s.terms || []).length; });
      return sendJson(res, {
        ok: true,
        folder: {
          ...folder,
          sets,
          total_words
        }
      });
    }

    // 9. Route: /share/:folderName hoặc /notebook/:folderName -> phục vụ student.html
    if (pathname.startsWith('/share/') || pathname.startsWith('/notebook/')) {
      const studentFile = path.join(PUBLIC_DIR, 'student.html');
      if (fs.existsSync(studentFile)) {
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
        return fs.createReadStream(studentFile).pipe(res);
      }
    }

    // 10. Phục vụ Static Files từ public/ (index.html, v.v.)
    let reqPath = pathname === '/' ? '/index.html' : pathname;
    const safePath = path.normalize(path.join(PUBLIC_DIR, reqPath));
    if (!safePath.startsWith(PUBLIC_DIR)) {
      res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
      return res.end('Forbidden');
    }

    if (fs.existsSync(safePath) && fs.statSync(safePath).isFile()) {
      const ext = path.extname(safePath).toLowerCase();
      const contentType = MIME_TYPES[ext] || 'application/octet-stream';
      res.writeHead(200, { 'Content-Type': contentType });
      return fs.createReadStream(safePath).pipe(res);
    }

    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('404 Not Found');
  });
});

server.listen(PORT, '0.0.0.0', () => {
  const localIp = getLocalIp();
  console.log('='.repeat(66));
  console.log('🚀 QUIZLET VN NODE.JS SERVER ĐANG CHẠY THÀNH CÔNG!');
  console.log('='.repeat(66));
  console.log(`👉 Truy cập máy này:           http://localhost:${PORT}`);
  console.log(`👉 Mạng nội bộ / Wi-Fi (LAN):  http://${localIp}:${PORT}`);
  console.log(`👉 Link học sinh chép từ mẫu:  http://${localIp}:${PORT}/share/IELTS%20%26%20H%E1%BB%8Dc%20thu%E1%BA%ADt`);
  console.log(`📁 Dữ liệu lưu tại:            ${DB_FILE}`);
  console.log('='.repeat(66));
});
