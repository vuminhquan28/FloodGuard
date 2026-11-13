import os
import subprocess
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_state_html(state_name, water, dist, rain_text, rain_color, adc_val, badge_cls, badge_text, pump_text, pump_col, valve_text, valve_col, buzzer_text, buzzer_col, bar_color):
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
    body {{ background: #070d1e; color: #ffffff; padding: 14px; width: 560px; height: 380px; }}
    .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; margin-bottom: 12px; }}
    .title {{ font-size: 1.05rem; font-weight: 800; color: #38bdf8; }}
    .badge-ip {{ font-size: 0.72rem; color: #94a3b8; background: rgba(56,189,248,0.12); border: 1px solid rgba(56,189,248,0.25); border-radius: 99px; padding: 2px 8px; }}
    
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }}
    .card {{ background: rgba(22, 33, 62, 0.75); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 10px; padding: 10px 12px; }}
    .card-title {{ font-size: 0.72rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 6px; }}
    .card-val {{ font-size: 1.6rem; font-weight: 800; line-height: 1.1; margin-bottom: 4px; }}
    .sub-text {{ font-size: 0.74rem; color: #cbd5e1; }}
    
    .bar-bg {{ width: 100%; height: 9px; background: rgba(255,255,255,0.08); border-radius: 5px; overflow: hidden; margin-top: 6px; }}
    .bar-fill {{ height: 100%; width: {water}%; background: {bar_color}; border-radius: 5px; }}
    
    .badge {{ display: inline-block; padding: 3px 8px; border-radius: 5px; font-weight: 700; font-size: 0.76rem; }}
    .badge-norm {{ background: rgba(16,185,129,0.2); color: #10b981; border: 1px solid #10b981; }}
    .badge-warn {{ background: rgba(245,158,11,0.2); color: #f59e0b; border: 1px solid #f59e0b; }}
    .badge-dang {{ background: rgba(239,68,68,0.25); color: #f87171; border: 1px solid #ef4444; }}
    .badge-crit {{ background: #ef4444; color: #ffffff; }}
    
    .row {{ display: flex; justify-content: space-between; font-size: 0.76rem; padding: 3px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }}
    .row:last-child {{ border: none; padding-bottom: 0; }}
    .ctrl-box {{ background: rgba(22, 33, 62, 0.75); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 10px; padding: 8px 12px; font-size: 0.72rem; }}
    .btn-row {{ display: flex; gap: 6px; margin-top: 6px; }}
    .btn {{ background: #1e293b; color: #cbd5e1; border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; padding: 4px 6px; font-size: 0.68rem; text-align: center; flex: 1; }}
    .btn-active {{ background: #2563eb; color: white; font-weight: 700; }}
  </style>
</head>
<body>
  <div class="header">
    <div class="title">FLOODGUARD DASHBOARD</div>
    <div class="badge-ip">📶 192.168.4.1 | AUTO</div>
  </div>
  <div class="grid">
    <div class="card">
      <div class="card-title">🌊 MỰC NƯỚC HỒ THU</div>
      <div class="card-val" style="color: {bar_color};">{water}%</div>
      <div class="sub-text">Cách mặt nước: <b>{dist} cm</b></div>
      <div class="bar-bg"><div class="bar-fill"></div></div>
    </div>
    <div class="card">
      <div class="card-title">⚠️ CẢNH BÁO & FSM</div>
      <div style="margin-bottom: 6px;">
        <span class="badge {badge_cls}">{badge_text}</span>
      </div>
      <div class="sub-text" style="line-height: 1.4;">
        <div>Mưa: <b style="color: {rain_color};">{rain_text}</b></div>
        <div>ADC: {adc_val} / 4095</div>
      </div>
    </div>
  </div>
  <div class="card" style="margin-bottom: 8px;">
    <div class="card-title">⚙️ THIẾT BỊ CHẤP HÀNH</div>
    <div class="row">
      <span style="color:#94a3b8;">Máy Bơm 5V:</span>
      <b style="color:{pump_col};">{pump_text}</b>
    </div>
    <div class="row">
      <span style="color:#94a3b8;">Cửa Van Xả:</span>
      <b style="color:{valve_col};">{valve_text}</b>
    </div>
    <div class="row">
      <span style="color:#94a3b8;">Còi Buzzer:</span>
      <b style="color:{buzzer_col};">{buzzer_text}</b>
    </div>
  </div>
  <div class="ctrl-box">
    <div style="color: #94a3b8; font-weight: 700; margin-bottom: 2px;">🎮 ĐIỀU KHIỂN CAN THIỆP TỪ XA</div>
    <div class="btn-row">
      <div class="btn btn-active">Chế Độ AUTO</div>
      <div class="btn">Bơm (Khóa)</div>
      <div class="btn">Van 0%</div>
      <div class="btn">Van 50%</div>
      <div class="btn">Van 100%</div>
    </div>
  </div>
</body>
</html>"""

def make_dashboard_4states():
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    states_meta = [
        ("state_a", "NORMAL", 15, "43.3", "KHÔNG MƯA", "#94a3b8", 3800, "badge-norm", "FSM: NORMAL", "ĐÃ TẮT (OFF)", "#94a3b8", "0% (ĐÓNG)", "#94a3b8", "YÊN LẶNG", "#94a3b8", "#10b981"),
        ("state_b", "WARNING", 35, "34.2", "MƯA NHỎ", "#38bdf8", 2550, "badge-warn", "FSM: WARNING", "ĐÃ TẮT (OFF)", "#94a3b8", "0% (ĐÓNG)", "#94a3b8", "BÍP THƯA", "#f59e0b", "#f59e0b"),
        ("state_c", "DANGER", 65, "20.8", "MƯA TO", "#f59e0b", 1420, "badge-dang", "FSM: DANGER", "ĐANG BẬT (ON)", "#10b981", "50% (MỞ NỬA)", "#38bdf8", "BÁO DỒN DẬP", "#f97316", "#f97316"),
        ("state_d", "CRITICAL", 85, "11.8", "MƯA CỰC TO / NGẬP", "#ef4444", 750, "badge-crit", "FSM: CRITICAL", "ĐANG BẬT (ON)", "#10b981", "100% (MỞ HẾT)", "#ef4444", "HÚ LIÊN TỤC", "#ef4444", "#ef4444")
    ]

    rendered_imgs = []
    for idx, (fn, st, w, d, rt, rc, adc, bc, bt, pt, pc, vt, vc, bzt, bzc, bar_c) in enumerate(states_meta):
        h = generate_state_html(st, w, d, rt, rc, adc, bc, bt, pt, pc, vt, vc, bzt, bzc, bar_c)
        tmp_h = os.path.abspath(f"figures/tmp_{fn}.html")
        tmp_p = os.path.abspath(f"figures/tmp_{fn}.png")
        with open(tmp_h, "w", encoding="utf-8") as f:
            f.write(h)
        
        cmd = [
            chrome,
            "--headless=new",
            "--hide-scrollbars",
            "--force-device-scale-factor=2",
            "--window-size=560,380",
            f"--screenshot={tmp_p}",
            f"file:///{tmp_h}"
        ]
        subprocess.run(cmd, capture_output=True)
        rendered_imgs.append(tmp_p)

    # Combine into 2x2 grid
    im_a = Image.open(rendered_imgs[0])
    im_b = Image.open(rendered_imgs[1])
    im_c = Image.open(rendered_imgs[2])
    im_d = Image.open(rendered_imgs[3])

    w, h = im_a.size
    grid_img = Image.new("RGB", (w * 2 + 40, h * 2 + 100), "#040816")
    draw = ImageDraw.Draw(grid_img)

    grid_img.paste(im_a, (15, 45))
    grid_img.paste(im_b, (w + 25, 45))
    grid_img.paste(im_c, (15, h + 85))
    grid_img.paste(im_d, (w + 25, h + 85))

    # Add titles on each panel
    try:
        font_label = ImageFont.truetype("arialbd.ttf", 26)
    except:
        font_label = ImageFont.load_default()

    draw.text((25, 12), "(a) Cấp 1: NORMAL (Bình thường - Mực nước 15%, Bơm TẮT, Van 0°)", fill="#10b981", font=font_label)
    draw.text((w + 35, 12), "(b) Cấp 2: WARNING (Cảnh báo - Mực nước 35%, Bơm TẮT, Còi bíp thưa)", fill="#f59e0b", font=font_label)
    draw.text((25, h + 52), "(c) Cấp 3: DANGER (Nguy cơ - Mực nước 65%, Bơm BẬT, Van mở 50%)", fill="#f97316", font=font_label)
    draw.text((w + 35, h + 52), "(d) Cấp 4: CRITICAL (Nguy cấp - Mực nước 85%, Bơm BẬT, Van mở 100%)", fill="#ef4444", font=font_label)

    out_p = "figures/dashboard_4states.png"
    rep_p = "report/figures/dashboard_4states.png"
    grid_img.save(out_p, quality=95)
    grid_img.save(rep_p, quality=95)
    print("Generated dashboard_4states.png successfully! Size:", grid_img.size)

    # Clean up temp files
    for fn in ["state_a", "state_b", "state_c", "state_d"]:
        for ext in [".html", ".png"]:
            p = f"figures/tmp_{fn}{ext}"
            if os.path.exists(p):
                os.remove(p)

def make_cloud_architecture():
    import textwrap
    fig, ax = plt.subplots(figsize=(16.0, 9.0), dpi=300)
    ax.set_xlim(0, 16.0)
    ax.set_ylim(0, 9.0)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Main title
    ax.text(8.0, 8.55, 'KIẾN TRÚC MỞ RỘNG ĐỀ XUẤT CHO HỆ THỐNG FLOODGUARD', fontsize=13.5, fontweight='bold', ha='center', va='center', color='#0f172a')
    ax.text(8.0, 8.20, 'Tích Hợp Truyền Thông Đám Mây MQTT/TLS, Giám Sát Tập Trung & Nguồn Dự Phòng An Toàn', fontsize=9.2, style='italic', color='#475569', ha='center', va='center')

    # Styles for minimalist, clean, low-color look
    zone_bg = '#f8fafc'
    zone_border = '#334155'
    box_bg = '#ffffff'
    box_border = '#64748b'
    text_title = '#0f172a'
    text_body = '#334155'
    subbox_bg = '#f1f5f9'
    subbox_border = '#94a3b8'

    # 3 Main Zones
    # Zone 1: x = 0.5 to 4.0 (w=3.5)
    # Gap 1:  x = 4.0 to 6.1 (w=2.1, center=5.05)
    # Zone 2: x = 6.1 to 9.8 (w=3.7, center=7.95)
    # Gap 2:  x = 9.8 to 11.9 (w=2.1, center=10.85)
    # Zone 3: x = 11.9 to 15.5 (w=3.6, center=13.70)
    z1 = patches.FancyBboxPatch((0.5, 0.5), 3.5, 7.1, boxstyle='round,pad=0.12', facecolor=zone_bg, edgecolor=zone_border, lw=1.3)
    z2 = patches.FancyBboxPatch((6.1, 0.5), 3.7, 7.1, boxstyle='round,pad=0.12', facecolor=zone_bg, edgecolor=zone_border, lw=1.3)
    z3 = patches.FancyBboxPatch((11.9, 0.5), 3.6, 7.1, boxstyle='round,pad=0.12', facecolor=zone_bg, edgecolor=zone_border, lw=1.3)
    ax.add_patch(z1)
    ax.add_patch(z2)
    ax.add_patch(z3)

    # Zone Headers
    ax.text(2.25, 7.20, 'TẦNG 1: TRẠM HIỆN TRƯỜNG\n(FIELD STATION HARDWARE)', fontsize=9.5, fontweight='bold', ha='center', va='center', color=text_title)
    ax.text(7.95, 7.20, 'TẦNG 2: MẠNG & AN TOÀN\n(SECURE IoT PROTOCOLS)', fontsize=9.5, fontweight='bold', ha='center', va='center', color=text_title)
    ax.text(13.70, 7.20, 'TẦNG 3: ĐÁM MÂY & GIÁM SÁT\n(CLOUD IoT PLATFORM)', fontsize=9.5, fontweight='bold', ha='center', va='center', color=text_title)

    # Separator lines
    for xc in [2.25, 7.95, 13.70]:
        ax.plot([xc - 1.45, xc + 1.45], [6.75, 6.75], color='#cbd5e1', lw=0.9)

    # Zone 1 contents: (x from 0.70 to 3.80, w=3.1)
    # Box 1: ESP32
    b_esp = patches.FancyBboxPatch((0.70, 3.95), 3.1, 2.55, boxstyle='round,pad=0.08', facecolor=box_bg, edgecolor=box_border, lw=1.1)
    ax.add_patch(b_esp)
    ax.text(2.25, 6.25, 'Vi Điều Khiển Trung Tâm ESP32', fontsize=9.0, fontweight='bold', ha='center', color=text_title)
    ax.text(2.25, 5.95, 'Kiến Trúc FreeRTOS Dual-Core (Station Mode)', fontsize=7.4, style='italic', ha='center', color='#64748b')

    c0 = patches.FancyBboxPatch((0.85, 4.15), 1.30, 1.55, boxstyle='round,pad=0.05', facecolor=subbox_bg, edgecolor=subbox_border, lw=0.9)
    c1 = patches.FancyBboxPatch((2.35, 4.15), 1.30, 1.55, boxstyle='round,pad=0.05', facecolor=subbox_bg, edgecolor=subbox_border, lw=0.9)
    ax.add_patch(c0)
    ax.add_patch(c1)
    ax.text(1.50, 5.45, 'Core 0 (Mạng)', fontsize=8.0, fontweight='bold', ha='center', color=text_title)
    ax.text(1.50, 4.75, '• MQTT Client\n• TLS 1.3 Stack\n• Network Task\n• REST API Server', fontsize=6.8, ha='center', va='center', color=text_body)

    ax.text(3.00, 5.45, 'Core 1 (Điều khiển)', fontsize=8.0, fontweight='bold', ha='center', color=text_title)
    ax.text(3.00, 4.75, '• FSM chu kỳ 200ms\n• Lọc trung vị 3 mẫu\n• Điều khiển Bơm/Van\n• Cảnh báo LED & Còi', fontsize=6.8, ha='center', va='center', color=text_body)

    # Box 2: Sensors
    b_sens = patches.FancyBboxPatch((0.70, 2.40), 3.1, 1.30, boxstyle='round,pad=0.08', facecolor=box_bg, edgecolor=box_border, lw=1.1)
    ax.add_patch(b_sens)
    ax.text(2.25, 3.42, 'Cảm Biến Dự Phòng & Biểu Quyết', fontsize=8.3, fontweight='bold', ha='center', color=text_title)
    ax.text(2.25, 2.90, '• Cảm biến chính: Siêu âm JSN-SR04T (IP67)\n• Cảm biến phụ: Áp suất thủy tĩnh / Phao từ\n• Thuật toán biểu quyết 2-out-of-2 (Voting)', fontsize=7.0, ha='center', va='center', color=text_body)

    # Box 3: Power & E-Stop
    b_pwr = patches.FancyBboxPatch((0.70, 0.85), 3.1, 1.30, boxstyle='round,pad=0.08', facecolor=box_bg, edgecolor=box_border, lw=1.1)
    ax.add_patch(b_pwr)
    ax.text(2.25, 1.87, 'Nguồn Dự Phòng & Dừng Khẩn Cấp', fontsize=8.3, fontweight='bold', ha='center', color=text_title)
    ax.text(2.25, 1.35, '• Nguồn kép: AC 220V + Pin lưu điện UPS/Solar\n• Tự động nạp đệm và chuyển mạch không ngắt\n• Nút cơ học E-Stop cắt nguồn cấp Relay', fontsize=7.0, ha='center', va='center', color=text_body)

    # Zone 2 contents: (x from 6.35 to 9.55, w=3.2)
    items_z2 = [
        ('Giao Thức MQTT over TLS 1.3', 'Mã hóa toàn diện đường truyền trên cổng 8883; xác thực bằng Client Certificate (X.509) chống nghe lén.', 5.25),
        ('Kênh Điều Khiển Tường Minh', 'Thay thế GET bằng HTTP POST hoặc MQTT Command Topic; truyền trạng thái tường minh (targetState = 1/0).', 3.80),
        ('Đường Truyền Kép (Dual Path)', 'Kết nối chính qua Wi-Fi Station; tự động chuyển vùng sang SIM 4G LTE / LoRaWAN khi mất kết nối trạm.', 2.35),
        ('Cơ Chế Heartbeat Độc Lập', 'Đếm nhịp Keep-alive 5s độc lập; tự động kích hoạt Failsafe thu hồi quyền MANUAL về AUTO sau 30s mất tín hiệu.', 0.85)
    ]
    for title, desc, yy in items_z2:
        bx = patches.FancyBboxPatch((6.35, yy), 3.2, 1.25, boxstyle='round,pad=0.08', facecolor=box_bg, edgecolor=box_border, lw=1.1)
        ax.add_patch(bx)
        ax.text(7.95, yy + 0.95, title, fontsize=8.2, fontweight='bold', ha='center', color=text_title)
        wrapped = textwrap.fill(desc, width=35)
        ax.text(7.95, yy + 0.48, wrapped, fontsize=6.9, ha='center', va='center', color=text_body)

    # Zone 3 contents: (x from 12.10 to 15.30, w=3.2)
    items_z3 = [
        ('IoT Cloud Platform & Broker', 'AWS IoT Core / EMQX / ThingsBoard CE tiếp nhận luồng telemetry với tốc độ xử lý hàng nghìn bản tin/giây.', 5.25),
        ('Cơ Sở Dữ Liệu Time-Series', 'InfluxDB / TimescaleDB lưu trữ toàn bộ chuỗi số liệu mực nước, lượng mưa và nhật ký tác động Failsafe.', 3.80),
        ('Bản Đồ Số GIS & SCADA', 'Giao diện bản đồ số trực quan theo dõi toàn mạng lưới trạm chống ngập, xem biểu đồ dâng nước và điều khiển tập trung.', 2.35),
        ('Hệ Thống Cảnh Báo Đa Kênh', 'Tích hợp Bot Telegram, Zalo OA và cổng SMS Gateway tự động nhắn tin cảnh báo cho người dân và cơ quan quản lý.', 0.85)
    ]
    for title, desc, yy in items_z3:
        bx = patches.FancyBboxPatch((12.10, yy), 3.2, 1.25, boxstyle='round,pad=0.08', facecolor=box_bg, edgecolor=box_border, lw=1.1)
        ax.add_patch(bx)
        ax.text(13.70, yy + 0.95, title, fontsize=8.2, fontweight='bold', ha='center', color=text_title)
        wrapped = textwrap.fill(desc, width=35)
        ax.text(13.70, yy + 0.48, wrapped, fontsize=6.9, ha='center', va='center', color=text_body)

    # Arrows & Labels with generous horizontal and vertical clearance:
    # Gap 1: from x = 4.0 to 6.1 (w=2.1, center=5.05)
    # Arrow 1: Uplink at y = 5.25
    ax.annotate('', xy=(5.95, 5.25), xytext=(4.15, 5.25),
                arrowprops=dict(arrowstyle='-|>', lw=1.4, color='#1e293b', mutation_scale=14))
    ax.text(5.05, 5.62, 'Publish Telemetry', fontsize=7.6, fontweight='bold', ha='center', va='bottom', color='#0f172a')
    ax.text(5.05, 4.88, 'Gói tin JSON chu kỳ 1s', fontsize=6.9, style='italic', ha='center', va='top', color='#475569')

    # Arrow 2: Downlink at y = 3.35
    ax.annotate('', xy=(4.15, 3.35), xytext=(5.95, 3.35),
                arrowprops=dict(arrowstyle='-|>', lw=1.4, color='#334155', linestyle='--', mutation_scale=14))
    ax.text(5.05, 3.72, 'Lệnh Can Thiệp Từ Xa', fontsize=7.6, fontweight='bold', ha='center', va='bottom', color='#0f172a')
    ax.text(5.05, 2.98, 'Bật/Tắt Bơm, Góc Van', fontsize=6.9, style='italic', ha='center', va='top', color='#475569')

    # Gap 2: from x = 9.8 to 11.9 (w=2.1, center=10.85)
    # Arrow 3: Uplink at y = 5.25
    ax.annotate('', xy=(11.75, 5.25), xytext=(9.95, 5.25),
                arrowprops=dict(arrowstyle='-|>', lw=1.4, color='#1e293b', mutation_scale=14))
    ax.text(10.85, 5.62, 'Giao Thức MQTT / TLS', fontsize=7.6, fontweight='bold', ha='center', va='bottom', color='#0f172a')
    ax.text(10.85, 4.88, 'Cổng 8883 (Mã hóa X.509)', fontsize=6.9, style='italic', ha='center', va='top', color='#475569')

    # Arrow 4: Downlink at y = 3.35
    ax.annotate('', xy=(9.95, 3.35), xytext=(11.75, 3.35),
                arrowprops=dict(arrowstyle='-|>', lw=1.4, color='#334155', linestyle='--', mutation_scale=14))
    ax.text(10.85, 3.72, 'Lệnh Giám Sát SCADA', fontsize=7.6, fontweight='bold', ha='center', va='bottom', color='#0f172a')
    ax.text(10.85, 2.98, 'Web App / GIS / Báo động', fontsize=6.9, style='italic', ha='center', va='top', color='#475569')

    out_p = "figures/proposed_cloud_architecture.png"
    rep_p = "report/figures/proposed_cloud_architecture.png"
    plt.savefig(out_p, dpi=300, bbox_inches='tight')
    plt.savefig(rep_p, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated proposed_cloud_architecture.png successfully!")

if __name__ == "__main__":
    make_dashboard_4states()
    make_cloud_architecture()
