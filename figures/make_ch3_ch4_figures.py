import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

out_dirs = [
    os.path.join("d:\\1. project\\FloodGuard", "figures"),
    os.path.join("d:\\1. project\\FloodGuard", "report", "figures")
]
for d in out_dirs:
    os.makedirs(d, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#000000'
plt.rcParams['axes.linewidth'] = 1.3
plt.rcParams['text.color'] = '#000000'

def save_fig(fig, filename):
    plt.tight_layout()
    for d in out_dirs:
        filepath = os.path.join(d, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Generated Figure: {filename}")

# =============================================================
# 1. FSM STATE MACHINE DIAGRAM (UML State Machine)
# 4 States: NORMAL, WARNING, DANGER, CRITICAL + SENSOR_FAULT
# =============================================================
def make_fsm_diagram():
    fig, ax = plt.subplots(figsize=(14.0, 7.8), dpi=300)
    ax.set_xlim(0, 14.0)
    ax.set_ylim(0, 7.8)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Title
    ax.text(7.0, 7.4, "SƠ ĐỒ CHUYỂN TRẠNG THÁI MÁY TRẠNG THÁI HỮU HẠN (FSM ENGINE)",
            fontsize=12.5, fontweight='bold', ha='center', va='center')

    # States positions
    # NORMAL (left), WARNING (mid-left), DANGER (mid-right), CRITICAL (right)
    states = [
        ("NORMAL\n(An Toàn)", 2.0, 4.0, "LED: Xanh\nBơm: OFF\nVan: 0°\nCòi: Tắt"),
        ("WARNING\n(Cảnh Báo)", 5.3, 4.0, "LED: Vàng\nBơm: OFF\nVan: 0°\nCòi: Bíp 1.5s"),
        ("DANGER\n(Nguy Hiểm)", 8.7, 4.0, "LED: Đỏ\nBơm: BẬT\nVan: 50% (90°)\nCòi: Dồn dập 300ms"),
        ("CRITICAL\n(Nguy Cấp)", 12.0, 4.0, "LED: Đỏ chớp\nBơm: BẬT\nVan: 100% (180°)\nCòi: Hú liên tục")
    ]

    box_w = 2.2
    box_h = 1.8

    for name, cx, cy, outputs in states:
        # Rounded state rectangle
        rect = patches.FancyBboxPatch((cx - box_w/2, cy - box_h/2), box_w, box_h,
                                      boxstyle="round,pad=0.1,rounding_size=0.2",
                                      edgecolor="#000000", facecolor="#f8f9fa", lw=1.5, zorder=3)
        ax.add_patch(rect)
        # Line separating title and outputs
        ax.plot([cx - box_w/2, cx + box_w/2], [cy + 0.25, cy + 0.25], color="#000000", lw=1.0, zorder=4)
        ax.text(cx, cy + 0.55, name, fontsize=10.0, fontweight='bold', ha='center', va='center', zorder=5)
        ax.text(cx, cy - 0.35, outputs, fontsize=8.2, ha='center', va='center', zorder=5)

    # Initial transition
    start_circle = plt.Circle((0.5, 4.0), 0.18, facecolor='#000000', edgecolor='#000000', zorder=4)
    ax.add_patch(start_circle)
    ax.annotate("", xy=(0.9, 4.0), xytext=(0.68, 4.0),
                arrowprops=dict(arrowstyle="->", lw=1.4, color="#000000"))

    # FORWARD TRANSITIONS (Top curved arcs)
    # NORMAL -> WARNING
    ax.annotate("", xy=(4.2, 4.6), xytext=(3.1, 4.6),
                arrowprops=dict(arrowstyle="->", lw=1.3, color="#000000",
                                connectionstyle="arc3,rad=-0.25"))
    ax.text(3.65, 5.25, "Nước ≥ 21%\nhoặc Mưa nhỏ", fontsize=8.2, fontweight='bold', ha='center', va='bottom')

    # WARNING -> DANGER
    ax.annotate("", xy=(7.6, 4.6), xytext=(6.4, 4.6),
                arrowprops=dict(arrowstyle="->", lw=1.3, color="#000000",
                                connectionstyle="arc3,rad=-0.25"))
    ax.text(7.0, 5.25, "Nước ≥ 41%\nhoặc Mưa to", fontsize=8.2, fontweight='bold', ha='center', va='bottom')

    # DANGER -> CRITICAL
    ax.annotate("", xy=(10.9, 4.6), xytext=(9.8, 4.6),
                arrowprops=dict(arrowstyle="->", lw=1.3, color="#000000",
                                connectionstyle="arc3,rad=-0.25"))
    ax.text(10.35, 5.25, "Nước ≥ 71%\nhoặc Ngập sensor", fontsize=8.2, fontweight='bold', ha='center', va='bottom')

    # BACKWARD TRANSITIONS WITH HYSTERESIS (Bottom curved arcs)
    # CRITICAL -> DANGER
    ax.annotate("", xy=(9.8, 3.4), xytext=(10.9, 3.4),
                arrowprops=dict(arrowstyle="->", lw=1.3, color="#000000", linestyle="--",
                                connectionstyle="arc3,rad=-0.25"))
    ax.text(10.35, 2.45, "Nước < 71%\n& Không ngập", fontsize=8.0, style='italic', ha='center', va='top')

    # DANGER -> WARNING
    ax.annotate("", xy=(6.4, 3.4), xytext=(7.6, 3.4),
                arrowprops=dict(arrowstyle="->", lw=1.3, color="#000000", linestyle="--",
                                connectionstyle="arc3,rad=-0.25"))
    ax.text(7.0, 2.45, "Nước < 40%\n& Không mưa to", fontsize=8.0, style='italic', ha='center', va='top')

    # WARNING -> NORMAL
    ax.annotate("", xy=(3.1, 3.4), xytext=(4.2, 3.4),
                arrowprops=dict(arrowstyle="->", lw=1.3, color="#000000", linestyle="--",
                                connectionstyle="arc3,rad=-0.25"))
    ax.text(3.65, 2.45, "Nước < 20%\n& Tạnh mưa", fontsize=8.0, style='italic', ha='center', va='top')

    # EXCEPTION: SENSOR_FAULT STATE
    fault_rect = patches.FancyBboxPatch((6.0, 0.4), 2.0, 1.1,
                                       boxstyle="round,pad=0.1,rounding_size=0.15",
                                       edgecolor="#000000", facecolor="#ffffff", lw=1.4, linestyle=":", zorder=3)
    ax.add_patch(fault_rect)
    ax.text(7.0, 1.15, "SENSOR_FAULT", fontsize=9.2, fontweight='bold', ha='center', va='center')
    ax.text(7.0, 0.70, "Lỗi Echo > 3 lần\nVan 50%, Còi báo lỗi", fontsize=7.8, ha='center', va='center')

    # Arrow from states down to fault
    ax.annotate("", xy=(6.8, 1.5), xytext=(7.0, 2.2),
                arrowprops=dict(arrowstyle="->", lw=1.1, linestyle=":", color="#000000"))
    ax.text(7.4, 1.8, "Mất tín hiệu\n> 600ms", fontsize=7.5, style='italic', ha='left', va='center')

    save_fig(fig, "fsm_state_machine.png")


# =============================================================
# 2. HYSTERESIS COMPARISON GRAPH
# Water oscillating around threshold: With vs Without Hysteresis
# =============================================================
def make_hysteresis_graph():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13.0, 7.5), dpi=300, sharex=True)
    fig.patch.set_facecolor('#ffffff')

    t = np.linspace(0, 30, 600)
    # Simulated water level oscillating around 40% threshold
    water = 38.0 + 4.0 * np.sin(0.8 * t) + 1.2 * np.sin(3.5 * t)

    # 1. Without Hysteresis (Threshold = 40.0% exactly)
    threshold = 40.0
    pump_no_hyst = np.zeros_like(water)
    for i in range(len(water)):
        pump_no_hyst[i] = 1.0 if water[i] >= threshold else 0.0

    ax1.plot(t, water, color='#000000', lw=1.6, label='Mực nước thực tế (%)')
    ax1.axhline(threshold, color='#666666', linestyle='--', lw=1.2, label='Ngưỡng cố định (40%)')
    ax1.step(t, pump_no_hyst * 8 + 48, color='#000000', lw=1.5, linestyle='-', label='Trạng thái Relay Bơm (ON/OFF)')
    ax1.set_ylabel('Mực nước & Relay', fontsize=10.5, fontweight='bold')
    ax1.set_title('A) Khi KHÔNG CÓ Dải Trễ (Hysteresis): Rung giật đóng/ngắt liên tục (Chattering)',
                  fontsize=11.0, fontweight='bold')
    ax1.set_ylim(32, 60)
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='upper right', fontsize=9.0)

    # Add text annotation pointing out chattering
    ax1.annotate('Hiện tượng rung giật\n(Bật/tắt 8 lần trong 10s!)', xy=(12.0, 48.0), xytext=(14.5, 54.0),
                 arrowprops=dict(arrowstyle="->", lw=1.2, color="#000000"),
                 fontsize=8.5, fontweight='bold')

    # 2. With Hysteresis (Enter = 41%, Exit = 38%)
    th_enter = 41.0
    th_exit = 38.0
    pump_hyst = np.zeros_like(water)
    state = 0.0
    for i in range(len(water)):
        if state == 0.0:
            if water[i] >= th_enter:
                state = 1.0
        else:
            if water[i] < th_exit:
                state = 0.0
        pump_hyst[i] = state

    ax2.plot(t, water, color='#000000', lw=1.6, label='Mực nước thực tế (%)')
    ax2.axhline(th_enter, color='#333333', linestyle='--', lw=1.2, label='Ngưỡng kích hoạt bật (41%)')
    ax2.axhline(th_exit, color='#666666', linestyle=':', lw=1.2, label='Ngưỡng hạ ngắt bơm (38%)')
    ax2.step(t, pump_hyst * 8 + 48, color='#000000', lw=1.8, label='Trạng thái Relay Bơm (ON/OFF)')
    ax2.set_xlabel('Thời gian t (giây)', fontsize=10.5, fontweight='bold')
    ax2.set_ylabel('Mực nước & Relay', fontsize=10.5, fontweight='bold')
    ax2.set_title('B) Khi CÓ Dải Trễ Hysteresis (Δ = 3%): Đóng/ngắt dứt khoát, triệt tiêu rung lắc',
                  fontsize=11.0, fontweight='bold')
    ax2.set_ylim(32, 60)
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='upper right', fontsize=9.0)

    # Add text annotation
    ax2.annotate('Bơm bật ổn định dứt điểm\nKhông bị tắt đột ngột', xy=(10.0, 56.0), xytext=(12.5, 54.0),
                 arrowprops=dict(arrowstyle="->", lw=1.2, color="#000000"),
                 fontsize=8.5, fontweight='bold')

    save_fig(fig, "hysteresis_response.png")


# =============================================================
# 3. SEQUENCE DIAGRAM FOR HTTP POLLING & CONTROL DISPATCH
# =============================================================
def make_sequence_diagram():
    fig, ax = plt.subplots(figsize=(13.5, 8.2), dpi=300)
    ax.set_xlim(0, 13.5)
    ax.set_ylim(0, 8.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    ax.text(6.75, 7.8, "SƠ ĐỒ TUẦN TỰ (UML SEQUENCE DIAGRAM) GIAO TIẾP WEB DASHBOARD",
            fontsize=12.0, fontweight='bold', ha='center', va='center')

    # Lifelines: User Browser (2.0), ESP32 Web Server (6.0), Hardware Actuator (10.5)
    lifelines = [
        ("Người Vận Hành\n(Web Browser)", 2.2),
        ("ESP32 Web Server\n(Port 80)", 6.75),
        ("Cơ Cấu Chấp Hành\n(Relay / Servo)", 11.2)
    ]

    for title, x in lifelines:
        rect = patches.Rectangle((x - 1.4, 6.7), 2.8, 0.8, facecolor="#f8f9fa", edgecolor="#000000", lw=1.3, zorder=3)
        ax.add_patch(rect)
        ax.text(x, 7.1, title, fontsize=9.5, fontweight='bold', ha='center', va='center', zorder=4)
        # Vertical dashed lifeline
        ax.plot([x, x], [6.7, 0.6], color="#555555", linestyle="--", lw=1.1, zorder=2)

    # Sequence 1: Polling Telemetry (Top section)
    ax.text(0.8, 6.2, "LUỒNG 1: GIÁM SÁT ĐỊNH KỲ (POLLING MỖI 1 GIÂY)", fontsize=9.5, fontweight='bold', color="#000000")

    # Arrow 1: Browser -> Server: GET /api/status
    ax.annotate("", xy=(6.75, 5.7), xytext=(2.2, 5.7),
                arrowprops=dict(arrowstyle="->", lw=1.3, color="#000000"))
    ax.text(4.45, 5.9, "1: HTTP GET /api/status", fontsize=8.8, ha='center', va='bottom')

    # Internal calculation on ESP32
    ax.plot([6.75, 7.2, 7.2, 6.75], [5.5, 5.5, 5.2, 5.2], color="#000000", lw=1.1)
    ax.text(7.35, 5.35, "2: Đóng gói JSON (telemetry,\nFSM state, pump, servo)", fontsize=8.0, va='center')

    # Arrow 2: Server -> Browser: HTTP 200 OK (JSON)
    ax.annotate("", xy=(2.2, 4.8), xytext=(6.75, 4.8),
                arrowprops=dict(arrowstyle="->", lw=1.3, linestyle="--", color="#000000"))
    ax.text(4.45, 5.0, "3: HTTP 200 OK {waterPercent, sysState, ...}", fontsize=8.5, ha='center', va='bottom')

    # Sequence 2: Control Command Dispatch (Bottom section)
    ax.text(0.8, 4.1, "LUỒNG 2: CAN THIỆP ĐIỀU KHIỂN CƯỠNG CHẾ (MANUAL OVERRIDE)", fontsize=9.5, fontweight='bold', color="#000000")

    # Arrow 3: User click button -> GET /api/control?action=pump_toggle
    ax.annotate("", xy=(6.75, 3.5), xytext=(2.2, 3.5),
                arrowprops=dict(arrowstyle="->", lw=1.3, color="#000000"))
    ax.text(4.45, 3.7, "4: HTTP GET /api/control?action=pump_toggle", fontsize=8.8, ha='center', va='bottom')

    # ESP32 checks condition
    ax.plot([6.75, 7.2, 7.2, 6.75], [3.3, 3.3, 3.0, 3.0], color="#000000", lw=1.1)
    ax.text(7.35, 3.15, "5: Kiểm tra !isAutoMode\nCập nhật pumpState", fontsize=8.0, va='center')

    # Arrow 4: ESP32 -> Hardware: digitalWrite(PIN_RELAY, LOW)
    ax.annotate("", xy=(11.2, 2.6), xytext=(6.75, 2.6),
                arrowprops=dict(arrowstyle="->", lw=1.3, color="#000000"))
    ax.text(8.95, 2.8, "6: GPIO 23 = LOW (Kích đóng Relay)", fontsize=8.5, ha='center', va='bottom')

    # Hardware response
    ax.plot([11.2, 11.6, 11.6, 11.2], [2.4, 2.4, 2.1, 2.1], color="#000000", lw=1.1)
    ax.text(11.75, 2.25, "7: Máy bơm mini 5V BẬT", fontsize=8.0, va='center')

    # Arrow 5: Server -> Browser: HTTP 200 OK
    ax.annotate("", xy=(2.2, 1.6), xytext=(6.75, 1.6),
                arrowprops=dict(arrowstyle="->", lw=1.3, linestyle="--", color="#000000"))
    ax.text(4.45, 1.8, "8: HTTP 200 OK \"OK\"", fontsize=8.5, ha='center', va='bottom')

    # UI updates immediately
    ax.plot([2.2, 1.7, 1.7, 2.2], [1.4, 1.4, 1.0, 1.0], color="#000000", lw=1.1)
    ax.text(1.6, 1.2, "9: Cập nhật DOM\nĐổi nút sang ĐANG BẬT", fontsize=8.0, ha='right', va='center')

    save_fig(fig, "sequence_diagram.png")


# =============================================================
# 4. DASHBOARD UI MOCKUP / WIREFRAME
# =============================================================
def make_dashboard_mockup():
    fig, ax = plt.subplots(figsize=(13.0, 8.2), dpi=300)
    ax.set_xlim(0, 13.0)
    ax.set_ylim(0, 8.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Outer browser window frame
    browser_frame = patches.Rectangle((0.5, 0.4), 12.0, 7.4, facecolor="#0b132b", edgecolor="#000000", lw=1.8, zorder=1)
    ax.add_patch(browser_frame)

    # Top browser bar
    browser_bar = patches.Rectangle((0.5, 7.3), 12.0, 0.5, facecolor="#1c2541", edgecolor="#000000", lw=1.0, zorder=2)
    ax.add_patch(browser_bar)

    # Window buttons
    for i, col in enumerate(["#ef4444", "#f59e0b", "#10b981"]):
        c = plt.Circle((0.8 + i*0.25, 7.55), 0.08, facecolor=col, edgecolor="#000000", lw=0.5, zorder=3)
        ax.add_patch(c)

    # URL Bar
    url_box = patches.Rectangle((2.2, 7.4), 8.5, 0.3, facecolor="#0b132b", edgecolor="#555555", lw=0.8, zorder=3)
    ax.add_patch(url_box)
    ax.text(2.4, 7.55, "http://192.168.4.1 (FloodGuard_AP) | mDNS: http://floodguard.local",
            fontsize=8.0, color="#38bdf8", va='center', zorder=4)

    # Title header
    ax.text(6.5, 6.9, "FLOODGUARD - GIÁM SÁT & CHỐNG NGẬP TỰ ĐỘNG",
            fontsize=12.0, fontweight='bold', color="#38bdf8", ha='center', va='center', zorder=4)
    ax.text(6.5, 6.6, "Hệ Thống Trạm IoT ESP32 - Chế Độ Mạng SoftAP Nội Bộ",
            fontsize=8.5, color="#94a3b8", ha='center', va='center', zorder=4)

    # 4 Cards in 2x2 grid
    # Card 1: Water Level (Top Left)
    c1 = patches.Rectangle((1.0, 3.8), 5.2, 2.5, facecolor="#1c2541", edgecolor=(1.0, 1.0, 1.0, 0.25), lw=1.2, zorder=3)
    ax.add_patch(c1)
    ax.text(1.2, 6.0, "GIÁM SÁT MỰC NƯỚC HỒ THU", fontsize=9.0, fontweight='bold', color="#94a3b8", zorder=4)
    ax.text(3.6, 5.3, "75%", fontsize=26.0, fontweight='bold', color="#ef4444", ha='center', va='center', zorder=4)
    ax.text(3.6, 4.6, "Khoảng cách: 16.2 cm | Đỉnh hồ: 5.0 cm", fontsize=8.5, color="#ffffff", ha='center', zorder=4)
    # Progress bar
    p_bg = patches.Rectangle((1.4, 4.1), 4.4, 0.25, facecolor="#334155", edgecolor="#000000", lw=0.5, zorder=4)
    p_fg = patches.Rectangle((1.4, 4.1), 3.3, 0.25, facecolor="#ef4444", edgecolor="#000000", lw=0.5, zorder=5)
    ax.add_patch(p_bg)
    ax.add_patch(p_fg)

    # Card 2: Rain Sensor & FSM State (Top Right)
    c2 = patches.Rectangle((6.8, 3.8), 5.2, 2.5, facecolor="#1c2541", edgecolor=(1.0, 1.0, 1.0, 0.25), lw=1.2, zorder=3)
    ax.add_patch(c2)
    ax.text(7.0, 6.0, "CẢM BIẾN MƯA & TRẠNG THÁI FSM", fontsize=9.0, fontweight='bold', color="#94a3b8", zorder=4)
    ax.text(9.4, 5.3, "MƯA TO (DANGER)", fontsize=13.0, fontweight='bold', color="#f59e0b", ha='center', zorder=4)
    ax.text(9.4, 4.7, "Điện áp ADC: 1420 / 4095 (Tương tự AO)", fontsize=8.5, color="#ffffff", ha='center', zorder=4)
    # Badge
    b1 = patches.FancyBboxPatch((8.2, 4.05), 2.4, 0.35, boxstyle="round,pad=0.05", facecolor="#ef4444", edgecolor="#000000", zorder=4)
    ax.add_patch(b1)
    ax.text(9.4, 4.22, "FSM: CRITICAL", fontsize=9.0, fontweight='bold', color="#ffffff", ha='center', va='center', zorder=5)

    # Card 3: Actuators Status (Bottom Left)
    c3 = patches.Rectangle((1.0, 0.9), 5.2, 2.6, facecolor="#1c2541", edgecolor=(1.0, 1.0, 1.0, 0.25), lw=1.2, zorder=3)
    ax.add_patch(c3)
    ax.text(1.2, 3.2, "TRẠNG THÁI THIẾT BỊ CHẤP HÀNH", fontsize=9.0, fontweight='bold', color="#94a3b8", zorder=4)
    ax.text(1.5, 2.7, "• Máy Bơm Thoát Nước 5V:", fontsize=8.5, color="#ffffff", zorder=4)
    ax.text(4.8, 2.7, "ĐANG BẬT", fontsize=9.0, fontweight='bold', color="#10b981", zorder=4)

    ax.text(1.5, 2.2, "• Cửa Van Thoát Lũ (Servo):", fontsize=8.5, color="#ffffff", zorder=4)
    ax.text(4.8, 2.2, "MỞ 100% (180°)", fontsize=9.0, fontweight='bold', color="#38bdf8", zorder=4)

    ax.text(1.5, 1.7, "• Còi Báo Động Buzzer:", fontsize=8.5, color="#ffffff", zorder=4)
    ax.text(4.8, 1.7, "HÚ LIÊN TỤC", fontsize=9.0, fontweight='bold', color="#ef4444", zorder=4)

    ax.text(1.5, 1.2, "• Chế Độ Điều Hành:", fontsize=8.5, color="#ffffff", zorder=4)
    ax.text(4.8, 1.2, "TỰ ĐỘNG (AUTO)", fontsize=9.0, fontweight='bold', color="#38bdf8", zorder=4)

    # Card 4: Control Buttons / Manual Override (Bottom Right)
    c4 = patches.Rectangle((6.8, 0.9), 5.2, 2.6, facecolor="#1c2541", edgecolor=(1.0, 1.0, 1.0, 0.25), lw=1.2, zorder=3)
    ax.add_patch(c4)
    ax.text(7.0, 3.2, "BẢNG ĐIỀU KHIỂN CAN THIỆP TỪ XA", fontsize=9.0, fontweight='bold', color="#94a3b8", zorder=4)

    # Button Mode Toggle
    btn1 = patches.FancyBboxPatch((7.2, 2.5), 4.4, 0.45, boxstyle="round,pad=0.05", facecolor="#3a86ff", edgecolor="#ffffff", lw=0.8, zorder=4)
    ax.add_patch(btn1)
    ax.text(9.4, 2.72, "Chuyển Sang Chế Độ Thủ Công (MANUAL)", fontsize=8.5, fontweight='bold', color="#ffffff", ha='center', va='center', zorder=5)

    # Button Pump Toggle (Disabled in AUTO)
    btn2 = patches.FancyBboxPatch((7.2, 1.85), 4.4, 0.45, boxstyle="round,pad=0.05", facecolor="#475569", edgecolor="#64748b", lw=0.8, zorder=4)
    ax.add_patch(btn2)
    ax.text(9.4, 2.07, "Bật / Tắt Bơm Thủ Công (Khóa ở AUTO)", fontsize=8.2, color="#94a3b8", ha='center', va='center', zorder=5)

    # 3 Buttons for Valve
    for i, (txt, bg) in enumerate([("Van 0°", "#475569"), ("Van 50%", "#475569"), ("Van 100%", "#475569")]):
        bx = 7.2 + i * 1.55
        btn_v = patches.FancyBboxPatch((bx, 1.2), 1.3, 0.45, boxstyle="round,pad=0.05", facecolor=bg, edgecolor="#64748b", lw=0.8, zorder=4)
        ax.add_patch(btn_v)
        ax.text(bx + 0.65, 1.42, txt, fontsize=8.0, color="#94a3b8", ha='center', va='center', zorder=5)

    save_fig(fig, "dashboard_mockup.png")

if __name__ == "__main__":
    print("Generating comprehensive Chapter 3 & 4 Figures...")
    make_fsm_diagram()
    make_hysteresis_graph()
    make_sequence_diagram()
    make_dashboard_mockup()
    print("All Figures for Chapter 3 & 4 generated successfully!")
