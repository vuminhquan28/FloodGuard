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
    fig, ax = plt.subplots(figsize=(14.0, 8.4), dpi=300)
    ax.set_xlim(0, 14.0)
    ax.set_ylim(0, 8.4)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Main title
    ax.text(7.0, 8.0, "KIẾN TRÚC MỞ RỘNG ĐỀ XUẤT CHO HỆ THỐNG FLOODGUARD", fontsize=14, fontweight='bold', ha='center', va='center')
    ax.text(7.0, 7.65, "Tích Hợp Truyền Thông Đám Mây MQTT/TLS, Giám Sát Tập Trung & Nguồn Dự Phòng An Toàn", fontsize=9.5, style='italic', color='#444444', ha='center', va='center')

    # 3 Main Zones
    # Zone 1: Trạm Hiện Trường (Left)
    z1 = patches.FancyBboxPatch((0.5, 0.6), 4.3, 6.7, boxstyle="round,pad=0.15", facecolor="#f8fafc", edgecolor="#0284c7", lw=1.8)
    ax.add_patch(z1)
    ax.text(2.65, 7.05, "TẦNG 1: TRẠNG HIỆN TRƯỜNG\n(FIELD STATION HARDWARE)", fontsize=9.5, fontweight='bold', ha='center', va='center', color="#0369a1")

    # Zone 2: An Toàn Truyền Thông (Middle)
    z2 = patches.FancyBboxPatch((5.1, 0.6), 3.8, 6.7, boxstyle="round,pad=0.15", facecolor="#f8fafc", edgecolor="#059669", lw=1.8)
    ax.add_patch(z2)
    ax.text(7.0, 7.05, "TẦNG 2: MẠNG & AN TOÀN\n(SECURE IoT PROTOCOLS)", fontsize=9.5, fontweight='bold', ha='center', va='center', color="#047857")

    # Zone 3: Hạ Tầng Đám Mây & Ứng Dụng (Right)
    z3 = patches.FancyBboxPatch((9.2, 0.6), 4.3, 6.7, boxstyle="round,pad=0.15", facecolor="#f8fafc", edgecolor="#7c3aed", lw=1.8)
    ax.add_patch(z3)
    ax.text(11.35, 7.05, "TẦNG 3: ĐÁM MÂY & GIÁM SÁT\n(CLOUD IoT PLATFORM)", fontsize=9.5, fontweight='bold', ha='center', va='center', color="#6d28d9")

    # Content in Zone 1 (Trạm hiện trường)
    # Box ESP32
    b_esp = patches.FancyBboxPatch((0.8, 3.8), 3.7, 2.7, boxstyle="round,pad=0.08", facecolor="#ffffff", edgecolor="#0284c7", lw=1.4)
    ax.add_patch(b_esp)
    ax.text(2.65, 6.2, "ESP32 SoC (Station Mode)", fontsize=10.0, fontweight='bold', ha='center', color="#0369a1")
    ax.text(2.65, 5.8, "FreeRTOS Dual-Core Architecture", fontsize=8.2, style='italic', ha='center', color="#555555")
    
    # Core 0 / Core 1
    c0 = patches.Rectangle((1.0, 4.0), 1.55, 1.5, facecolor="#eff6ff", edgecolor="#93c5fd", lw=1.0)
    ax.add_patch(c0)
    ax.text(1.77, 5.15, "Core 0", fontsize=8.5, fontweight='bold', ha='center', color="#1e40af")
    ax.text(1.77, 4.65, "Network Task\nMQTT Client\nTLS 1.3 Stack", fontsize=7.2, ha='center')

    c1 = patches.Rectangle((2.75, 4.0), 1.55, 1.5, facecolor="#eff6ff", edgecolor="#93c5fd", lw=1.0)
    ax.add_patch(c1)
    ax.text(3.52, 5.15, "Core 1", fontsize=8.5, fontweight='bold', ha='center', color="#1e40af")
    ax.text(3.52, 4.65, "FSM Control\nMedian Filter\nActuator Drive", fontsize=7.2, ha='center')

    # Sensors Box with redundancy
    b_sens = patches.FancyBboxPatch((0.8, 2.3), 3.7, 1.25, boxstyle="round,pad=0.08", facecolor="#ffffff", edgecolor="#475569", lw=1.2)
    ax.add_patch(b_sens)
    ax.text(2.65, 3.25, "Hệ Thống Cảm Biến Dự Phòng (Redundant)", fontsize=8.5, fontweight='bold', ha='center')
    ax.text(2.65, 2.7, "• Cảm biến chính: Siêu âm JSN-SR04T (IP67)\n• Cảm biến dự phòng: Áp suất / Phao từ\n• Thuật toán biểu quyết 2-out-of-2 (Voting)", fontsize=7.2, ha='center')

    # Power & E-stop Box
    b_pwr = patches.FancyBboxPatch((0.8, 0.8), 3.7, 1.25, boxstyle="round,pad=0.08", facecolor="#ffffff", edgecolor="#ef4444", lw=1.2)
    ax.add_patch(b_pwr)
    ax.text(2.65, 1.75, "Khối Nguồn & Dừng Khẩn Cấp (Safety)", fontsize=8.5, fontweight='bold', ha='center', color="#dc2626")
    ax.text(2.65, 1.2, "• Nguồn lưới 220V AC + Bộ sạc tự động\n• Pin lưu điện UPS / Solar Panel 12V DC\n• Nút nhấn cơ học E-Stop cắt trực tiếp Relay", fontsize=7.2, ha='center')

    import textwrap
    # Content in Zone 2 (An toàn truyền thông)
    items_z2 = [
        ("Giao Thức MQTT over TLS 1.3", "Mã hóa toàn diện đường truyền trên cổng 8883; xác thực bằng Client Certificate (X.509) chống nghe lén và giả mạo.", 5.3),
        ("Kênh Điều Khiển Tường Minh", "Thay thế GET bằng HTTP POST hoặc MQTT Command Topic; lệnh mang trạng thái rõ ràng (targetState = 1/0).", 3.8),
        ("Đường Truyền Sao Lưu (Dual Path)", "Kết nối chính qua Wi-Fi Station; tự động chuyển vùng sang SIM 4G LTE / LoRaWAN khi mất kết nối cáp quang.", 2.3),
        ("Cơ Chế Heartbeat Độc Lập", "Đếm nhịp Keep-alive chuyên biệt 5s; tự động kích hoạt Failsafe thu hồi quyền MANUAL nếu mất tín hiệu điều khiển.", 0.8)
    ]
    for title, desc, yy in items_z2:
        bx = patches.FancyBboxPatch((5.3, yy), 3.4, 1.25, boxstyle="round,pad=0.08", facecolor="#ffffff", edgecolor="#059669", lw=1.2)
        ax.add_patch(bx)
        ax.text(7.0, yy + 0.95, title, fontsize=8.2, fontweight='bold', ha='center', color="#047857")
        wrapped = textwrap.fill(desc, width=34)
        ax.text(7.0, yy + 0.50, wrapped, fontsize=7.0, ha='center', va='center')

    # Content in Zone 3 (Đám mây & Giám sát)
    items_z3 = [
        ("IoT Cloud Platform / Broker", "AWS IoT Core / EMQX / ThingsBoard CE tiếp nhận luồng telemetry với tốc độ xử lý hàng nghìn bản tin/giây.", 5.3),
        ("Cơ Sở Dữ Liệu Time-Series", "InfluxDB / TimescaleDB lưu trữ toàn bộ chuỗi số liệu mực nước, lượng mưa và nhật ký tác động Failsafe.", 3.8),
        ("Bản Đồ Số GIS & Web Dashboard", "Giao diện bản đồ số trực quan theo dõi toàn mạng lưới trạm chống ngập, xem biểu đồ dâng nước và điều khiển tập trung.", 2.3),
        ("Hệ Thống Cảnh Báo Khẩn", "Tích hợp Bot Telegram, Zalo OA và cổng SMS Gateway tự động nhắn tin cảnh báo cho người dân và cơ quan quản lý.", 0.8)
    ]
    for title, desc, yy in items_z3:
        bx = patches.FancyBboxPatch((9.4, yy), 3.9, 1.25, boxstyle="round,pad=0.08", facecolor="#ffffff", edgecolor="#7c3aed", lw=1.2)
        ax.add_patch(bx)
        ax.text(11.35, yy + 0.95, title, fontsize=8.2, fontweight='bold', ha='center', color="#6d28d9")
        wrapped = textwrap.fill(desc, width=40)
        ax.text(11.35, yy + 0.50, wrapped, fontsize=7.0, ha='center', va='center')

    # Interconnecting Arrows
    # Zone 1 -> Zone 2
    ax.annotate("", xy=(5.25, 5.18), xytext=(4.55, 5.18), arrowprops=dict(arrowstyle="->", lw=1.6, color="#0284c7"))
    ax.annotate("", xy=(4.55, 3.65), xytext=(5.25, 3.65), arrowprops=dict(arrowstyle="->", lw=1.6, color="#059669", linestyle="--"))
    ax.text(4.90, 5.30, "Publish", fontsize=6.8, ha='center', fontweight='bold', color="#0284c7")
    ax.text(4.90, 3.48, "Command", fontsize=6.8, ha='center', fontweight='bold', color="#059669")

    # Zone 2 -> Zone 3
    ax.annotate("", xy=(9.35, 5.18), xytext=(8.75, 5.18), arrowprops=dict(arrowstyle="->", lw=1.6, color="#059669"))
    ax.annotate("", xy=(8.75, 3.65), xytext=(9.35, 3.65), arrowprops=dict(arrowstyle="->", lw=1.6, color="#7c3aed", linestyle="--"))
    ax.text(9.05, 5.30, "TLS 8883", fontsize=6.8, ha='center', fontweight='bold', color="#059669")
    ax.text(9.05, 3.48, "Control", fontsize=6.8, ha='center', fontweight='bold', color="#7c3aed")

    out_p = "figures/proposed_cloud_architecture.png"
    rep_p = "report/figures/proposed_cloud_architecture.png"
    plt.savefig(out_p, dpi=300, bbox_inches='tight')
    plt.savefig(rep_p, dpi=300, bbox_inches='tight')
    plt.close()
    print("Generated proposed_cloud_architecture.png successfully!")

if __name__ == "__main__":
    make_dashboard_4states()
    make_cloud_architecture()
