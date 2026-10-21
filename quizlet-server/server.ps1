<#
  QuizletVN Server cho Windows (PowerShell - Không cần cài Python hay Node.js)
  Chạy trực tiếp trên mọi máy Windows 7, 8, 10, 11
#>

$port = 8000
$baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$publicDir = Join-Path $baseDir "public"
$dbDir = Join-Path $baseDir "database"
$dbFile = Join-Path $dbDir "quizlet_data.json"

if (-not (Test-Path $dbDir)) { New-Item -ItemType Directory -Path $dbDir -Force | Out-Null }
if (-not (Test-Path $publicDir)) { New-Item -ItemType Directory -Path $publicDir -Force | Out-Null }

# Lấy địa chỉ IP mạng LAN/Wi-Fi
$localIp = "127.0.0.1"
try {
    $ipAddresses = [System.Net.Dns]::GetHostAddresses([System.Net.Dns]::GetHostName()) | Where-Object { $_.AddressFamily -eq 'InterNetwork' -and $_.IPAddressToString -notlike '127.*' }
    if ($ipAddresses) { $localIp = $ipAddresses[0].IPAddressToString }
} catch {}

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
$listener.Prefixes.Add("http://127.0.0.1:$port/")

try {
    $listener.Start()
} catch {
    Write-Host "Không thể mở cổng $port (Có thể cổng đang bận hoặc cần quyền Admin). Đang thử cổng 8080..." -ForegroundColor Yellow
    $port = 8080
    $listener = New-Object System.Net.HttpListener
    $listener.Prefixes.Add("http://localhost:$port/")
    $listener.Prefixes.Add("http://127.0.0.1:$port/")
    $listener.Start()
}

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "🚀 MÁY CHỦ QUIZLET VN ĐANG CHẠY THÀNH CÔNG (POWERSHELL NATIVE)!" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "👉 Truy cập trên máy này:        http://localhost:$port" -ForegroundColor Yellow
Write-Host "👉 Truy cập mạng LAN/Wi-Fi:     http://${localIp}:$port" -ForegroundColor Yellow
Write-Host "👉 Link học sinh chép từ:       http://${localIp}:${port}/share/IELTS%20%26%20H%E1%BB%8Dc%20thu%E1%BA%ADt" -ForegroundColor Yellow
Write-Host "📁 CSDL lưu tại:                $dbFile" -ForegroundColor Gray
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "Nhấn phím Ctrl + C để dừng máy chủ bất cứ lúc nào.`n"

# Tự động mở trình duyệt web
Start-Process "http://localhost:$port"

# Vòng lặp lắng nghe request
while ($listener.IsListening) {
    try {
        $context = $listener.GetContext()
        $request = $context.Request
        $response = $context.Response
        $rawPath = $request.Url.AbsolutePath
        $method = $request.HttpMethod

        $response.AddHeader("Access-Control-Allow-Origin", "*")
        $response.AddHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        $response.AddHeader("Access-Control-Allow-Headers", "Content-Type, Authorization")

        if ($method -eq "OPTIONS") {
            $response.StatusCode = 204
            $response.Close()
            continue
        }

        # 1. API GET /api/folders
        if ($method -eq "GET" -and $rawPath -eq "/api/folders") {
            $json = "{}"
            if (Test-Path $dbFile) { $json = Get-Content -Path $dbFile -Raw -Encoding UTF8 }
            $obj = $json | ConvertFrom-Json -ErrorAction SilentlyContinue
            $folders = if ($obj -and $obj.folders) { $obj.folders } else { @() }
            $resPayload = @{ ok = $true; folders = $folders } | ConvertTo-Json -Depth 6
            $buf = [System.Text.Encoding]::UTF8.GetBytes($resPayload)
            $response.ContentType = "application/json; charset=utf-8"
            $response.ContentLength64 = $buf.Length
            $response.OutputStream.Write($buf, 0, $buf.Length)
            $response.Close()
            continue
        }

        # 2. API GET /api/sets
        if ($method -eq "GET" -and $rawPath -eq "/api/sets") {
            $json = "{}"
            if (Test-Path $dbFile) { $json = Get-Content -Path $dbFile -Raw -Encoding UTF8 }
            $obj = $json | ConvertFrom-Json -ErrorAction SilentlyContinue
            $sets = if ($obj -and $obj.study_sets) { $obj.study_sets } else { @() }
            $resPayload = @{ ok = $true; sets = $sets } | ConvertTo-Json -Depth 6
            $buf = [System.Text.Encoding]::UTF8.GetBytes($resPayload)
            $response.ContentType = "application/json; charset=utf-8"
            $response.ContentLength64 = $buf.Length
            $response.OutputStream.Write($buf, 0, $buf.Length)
            $response.Close()
            continue
        }

        # 3. Route /share/:name hoặc /notebook/:name
        if ($rawPath.StartsWith("/share/") -or $rawPath.StartsWith("/notebook/")) {
            $studentHtml = Join-Path $publicDir "student.html"
            if (Test-Path $studentHtml) {
                $buf = [System.IO.File]::ReadAllBytes($studentHtml)
                $response.ContentType = "text/html; charset=utf-8"
                $response.ContentLength64 = $buf.Length
                $response.OutputStream.Write($buf, 0, $buf.Length)
                $response.Close()
                continue
            }
        }

        # 4. Phục vụ Static Files từ public/ (index.html, v.v.)
        $subPath = if ($rawPath -eq "/") { "index.html" } else { $rawPath.TrimStart('/') }
        $filePath = Join-Path $publicDir $subPath

        if (Test-Path $filePath -PathType Leaf) {
            $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
            $mime = switch ($ext) {
                ".html" { "text/html; charset=utf-8" }
                ".css"  { "text/css; charset=utf-8" }
                ".js"   { "application/javascript; charset=utf-8" }
                ".json" { "application/json; charset=utf-8" }
                ".png"  { "image/png" }
                ".jpg"  { "image/jpeg" }
                ".svg"  { "image/svg+xml" }
                default { "application/octet-stream" }
            }
            $buf = [System.IO.File]::ReadAllBytes($filePath)
            $response.ContentType = $mime
            $response.ContentLength64 = $buf.Length
            $response.OutputStream.Write($buf, 0, $buf.Length)
            $response.Close()
            continue
        }

        $response.StatusCode = 404
        $msg = [System.Text.Encoding]::UTF8.GetBytes("404 Not Found")
        $response.OutputStream.Write($msg, 0, $msg.Length)
        $response.Close()
    } catch {
        # Bỏ qua lỗi ngắt kết nối
    }
}
