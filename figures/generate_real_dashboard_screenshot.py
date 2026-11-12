import os
import subprocess
import time
from PIL import Image

def generate_dashboard_image():
    html_content = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>FloodGuard Station - 192.168.4.1</title>
  <style>
    :root {
      --bg: #070d1e;
      --card-bg: rgba(22, 33, 62, 0.72);
      --card-border: rgba(255, 255, 255, 0.12);
      --text: #ffffff;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --green: #10b981;
      --yellow: #f59e0b;
      --orange: #f97316;
      --red: #ef4444;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    
    body {
      background: #040816;
      color: var(--text);
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 16px;
      margin: 0;
    }

    /* Window Container (Realistic Browser Frame) */
    .browser-window {
      width: 100%;
      max-width: 1120px;
      background: var(--bg);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.12);
    }

    /* Browser Header / Chrome Bar */
    .browser-header {
      background: #111827;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      padding: 10px 16px;
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .window-dots {
      display: flex;
      gap: 7px;
    }
    .dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
    }
    .dot-close { background: #ff5f56; border: 1px solid #e0443e; }
    .dot-min   { background: #ffbd2e; border: 1px solid #dea123; }
    .dot-max   { background: #27c93f; border: 1px solid #1aab29; }

    .browser-nav-icons {
      display: flex;
      gap: 10px;
      color: #64748b;
      font-size: 14px;
    }
    .nav-btn {
      cursor: pointer;
      user-select: none;
    }

    .address-bar {
      flex: 1;
      background: #1e293b;
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      padding: 6px 14px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.86rem;
      color: #cbd5e1;
    }
    .url-text {
      display: flex;
      align-items: center;
      gap: 8px;
      font-family: 'Consolas', 'Courier New', monospace;
    }
    .lock-icon {
      color: #10b981;
      font-size: 0.8rem;
    }
    .mdns-tag {
      background: rgba(56, 189, 248, 0.15);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.3);
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 600;
    }

    /* Web Content Container */
    .dashboard-viewport {
      padding: 30px 36px 36px 36px;
      background: radial-gradient(circle at 50% 10%, rgba(56, 189, 248, 0.08) 0%, transparent 60%),
                  radial-gradient(circle at 90% 80%, rgba(59, 130, 246, 0.05) 0%, transparent 50%),
                  #070d1e;
    }

    header {
      text-align: center;
      margin-bottom: 26px;
    }
    header h1 {
      font-size: 2.0rem;
      font-weight: 800;
      color: #38bdf8;
      letter-spacing: 1.2px;
      text-shadow: 0 0 24px rgba(56, 189, 248, 0.35);
    }
    header p {
      color: var(--text-muted);
      font-size: 0.95rem;
      margin-top: 5px;
    }
    .network-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(56, 189, 248, 0.12);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.3);
      border-radius: 999px;
      padding: 5px 14px;
      font-size: 0.80rem;
      font-weight: 600;
      margin-top: 10px;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 18px;
      margin-bottom: 20px;
    }

    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 20px;
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    }
    .card-title {
      font-size: 0.85rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      color: #94a3b8;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .card-value {
      font-size: 2.2rem;
      font-weight: 800;
      line-height: 1.1;
      margin-bottom: 6px;
      color: #ffffff;
    }

    .progress-bar-bg {
      width: 100%;
      height: 14px;
      background: rgba(255, 255, 255, 0.08);
      border-radius: 7px;
      overflow: hidden;
      margin-top: 10px;
      border: 1px solid rgba(255, 255, 255, 0.06);
    }
    .progress-bar {
      height: 100%;
      width: 75%;
      background: linear-gradient(90deg, #f59e0b, #ef4444);
      box-shadow: 0 0 14px rgba(239, 68, 68, 0.6);
      border-radius: 7px;
    }

    .status-badge {
      display: inline-block;
      padding: 5px 12px;
      border-radius: 6px;
      font-weight: 700;
      font-size: 0.90rem;
      letter-spacing: 0.5px;
    }
    .badge-normal   { background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }
    .badge-warning  { background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b; }
    .badge-danger   { background: rgba(239, 68, 68, 0.25); color: #f87171; border: 1px solid #ef4444; box-shadow: 0 0 12px rgba(239, 68, 68, 0.35); }
    .badge-critical { background: #ef4444; color: white; }

    .device-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 7px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      font-size: 0.92rem;
    }
    .device-row:last-child {
      border-bottom: none;
      padding-bottom: 0;
    }
    .device-label {
      color: #cbd5e1;
    }
    .device-state {
      font-weight: 700;
    }

    /* Control Panel */
    .control-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 20px 24px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    }
    .control-desc {
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-bottom: 16px;
    }
    .btn-group {
      display: flex;
      flex-wrap: nowrap;
      gap: 10px;
    }
    .control-btn {
      background: #1e293b;
      color: white;
      border: 1px solid rgba(255, 255, 255, 0.15);
      padding: 10px 12px;
      border-radius: 8px;
      font-weight: 600;
      cursor: pointer;
      font-size: 0.82rem;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      white-space: nowrap;
      flex: 1;
      transition: all 0.2s ease;
    }
    .btn-primary {
      background: #2563eb;
      border-color: #3b82f6;
      box-shadow: 0 0 14px rgba(37, 99, 235, 0.4);
    }
    .btn-danger {
      background: #dc2626;
      border-color: #ef4444;
      box-shadow: 0 0 14px rgba(220, 38, 38, 0.4);
    }
    .btn-muted {
      background: #1e293b;
      color: #64748b;
      border-color: rgba(255, 255, 255, 0.08);
    }
    .btn-active-valve {
      background: #0284c7;
      border-color: #38bdf8;
      box-shadow: 0 0 12px rgba(2, 132, 199, 0.4);
    }
  </style>
</head>
<body>

  <div class="browser-window">
    <!-- Chrome Frame Navigation Bar -->
    <div class="browser-header">
      <div class="window-dots">
        <div class="dot dot-close"></div>
        <div class="dot dot-min"></div>
        <div class="dot dot-max"></div>
      </div>
      <div class="browser-nav-icons">
        <span class="nav-btn">&#x2190;</span>
        <span class="nav-btn">&#x2192;</span>
        <span class="nav-btn">&#x21bb;</span>
      </div>
      <div class="address-bar">
        <div class="url-text">
          <span class="lock-icon">&#128274;</span>
          <span>http://192.168.4.1/</span>
          <span style="color: #64748b; font-size: 0.78rem;">(FloodGuard SoftAP Gateway)</span>
        </div>
        <div class="mdns-tag">mDNS: floodguard.local</div>
      </div>
    </div>

    <!-- Live Dashboard Content -->
    <div class="dashboard-viewport">
      <header>
        <h1>FLOODGUARD DASHBOARD</h1>
        <p>Hệ Thống Trạm IoT Giám Sát & Chống Ngập Thông Minh (ESP32 AP Mode)</p>
        <div class="network-badge">
          <span>📶</span> Wi-Fi: FloodGuard_AP &nbsp;|&nbsp; IP: 192.168.4.1 &nbsp;|&nbsp; Trạng thái: KẾT NỐI TRỰC TIẾP
        </div>
      </header>

      <div class="grid">
        <!-- Khối 1: Mực nước -->
        <div class="card">
          <div class="card-title">
            <span>🌊</span> MỰC NƯỚC HỒ THU
          </div>
          <div class="card-value" style="color: #f87171;">75%</div>
          <div style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 4px;">
            Khoảng cách: <b style="color: #ffffff;">16.2 cm</b> <span style="font-size: 0.76rem; color: #64748b;">(Đỉnh hồ: 5.0 cm | Đáy: 50.0 cm)</span>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar"></div>
          </div>
        </div>

        <!-- Khối 2: Cảnh báo & FSM -->
        <div class="card">
          <div class="card-title">
            <span>⚠️</span> CẢNH BÁO & TRẠNG THÁI FSM
          </div>
          <div style="margin-bottom: 12px; display: flex; align-items: center; gap: 10px;">
            <span class="status-badge badge-danger">FSM: DANGER</span>
            <span class="status-badge badge-normal" style="font-size: 0.78rem; padding: 4px 8px;">CHẾ ĐỘ: AUTO</span>
          </div>
          <div style="font-size: 0.88rem; color: var(--text-muted); line-height: 1.5;">
            <div>Thời tiết: <b style="color: #f59e0b;">MƯA TO (CẢNH BÁO)</b></div>
            <div>Điện áp ADC FC-37: <b style="color: #cbd5e1;">1420 / 4095</b> (Ngưỡng &lt; 1800)</div>
          </div>
        </div>

        <!-- Khối 3: Thiết bị chấp hành -->
        <div class="card">
          <div class="card-title">
            <span>⚙️</span> TRẠNG THÁI THIẾT BỊ CHẤP HÀNH
          </div>
          <div class="device-row">
            <span class="device-label">Máy Bơm 5V:</span>
            <span class="device-state" style="color: #10b981;">ĐANG BẬT (ON)</span>
          </div>
          <div class="device-row">
            <span class="device-label">Cửa Van Thoát Lũ:</span>
            <span class="device-state" style="color: #38bdf8;">MỞ 100% (180°)</span>
          </div>
          <div class="device-row">
            <span class="device-label">Còi Báo Buzzer:</span>
            <span class="device-state" style="color: #ef4444;">HÚ DỒN DẬP</span>
          </div>
        </div>
      </div>

      <!-- Khối 4: Bảng điều khiển từ xa -->
      <div class="control-card">
        <div class="card-title" style="margin-bottom: 6px;">
          <span>🎮</span> BẢNG ĐIỀU KHIỂN CAN THIỆP TỪ XA (MANUAL OVERRIDE CONTROLS)
        </div>
        <p class="control-desc">
          Hệ thống đang hoạt động ở chế độ <b>AUTO</b> (thuật toán FSM tự động ra quyết định). Nhấn <b>Đổi Chế Độ</b> để kích hoạt can thiệp thủ công từ xa.
        </p>
        <div class="btn-group">
          <button class="control-btn btn-primary">
            <span>🔄</span> Đổi Chế Độ (AUTO / MANUAL)
          </button>
          <button class="control-btn btn-muted" title="Chỉ kích hoạt khi ở chế độ MANUAL">
            <span>⚡</span> Bật / Tắt Máy Bơm (Khóa ở AUTO)
          </button>
          <button class="control-btn btn-muted">
            <span>🔒</span> Van 0% (Đóng)
          </button>
          <button class="control-btn btn-muted">
            <span>⚡</span> Van 50% (Mở Nửa)
          </button>
          <button class="control-btn btn-active-valve">
            <span>🚀</span> Van 100% (Mở Hết)
          </button>
        </div>
      </div>
    </div>
  </div>

</body>
</html>
"""
    tmp_html = os.path.abspath("figures/render_dashboard_screen.html")
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    out_img = os.path.abspath("figures/dashboard_mockup.png")
    report_img = os.path.abspath("report/figures/dashboard_mockup.png")

    # High-resolution capture: 1200x820 viewport with 2x device scale -> 2400x1640 ultra-sharp PNG
    cmd = [
        chrome,
        "--headless=new",
        "--hide-scrollbars",
        "--force-device-scale-factor=2",
        "--window-size=1160,780",
        f"--screenshot={out_img}",
        f"file:///{tmp_html}"
    ]
    print("Running Chrome to capture dashboard screenshot...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("Chrome error:", res.stderr)
        return False

    if not os.path.exists(out_img):
        print("Screenshot file was not generated!")
        return False

    # Also copy to report/figures/dashboard_mockup.png
    import shutil
    shutil.copyfile(out_img, report_img)
    print(f"Generated {out_img} and {report_img} successfully!")
    im = Image.open(out_img)
    print("Image size:", im.size, "Format:", im.format)
    return True

if __name__ == "__main__":
    generate_dashboard_image()
