import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import os

out_dirs = [
    os.path.join("d:\\1. project\\FloodGuard", "figures"),
    os.path.join("d:\\1. project\\FloodGuard", "report", "figures")
]
for d in out_dirs:
    os.makedirs(d, exist_ok=True)

# Set high quality black and white font & style
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#000000'
plt.rcParams['axes.linewidth'] = 1.2
plt.rcParams['text.color'] = '#000000'

def save_fig(fig, filename):
    plt.tight_layout()
    for d in out_dirs:
        fig.savefig(os.path.join(d, filename), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Generated B&W: {filename}")

def draw_stick_figure(ax, x, y, label, sublabel=None, scale=1.0):
    r = 0.22 * scale
    head = plt.Circle((x, y + 0.38 * scale), r, facecolor='#ffffff', edgecolor='#000000', lw=1.3, zorder=5)
    ax.add_patch(head)
    # Body
    ax.plot([x, x], [y + 0.16 * scale, y - 0.32 * scale], color='#000000', lw=1.4, zorder=5)
    # Arms
    ax.plot([x - 0.28 * scale, x + 0.28 * scale], [y - 0.02 * scale, y - 0.02 * scale], color='#000000', lw=1.4, zorder=5)
    # Legs
    ax.plot([x, x - 0.24 * scale], [y - 0.32 * scale, y - 0.7 * scale], color='#000000', lw=1.4, zorder=5)
    ax.plot([x, x + 0.24 * scale], [y - 0.32 * scale, y - 0.7 * scale], color='#000000', lw=1.4, zorder=5)
    # Label
    ax.text(x, y - 0.85 * scale, label, fontsize=9, fontweight='bold', ha='center', va='top', color='#000000')
    if sublabel:
        ax.text(x, y - 1.15 * scale, sublabel, fontsize=7.5, style='italic', ha='center', va='top', color='#333333')

def draw_subsystem_box(ax, x, y, w, h, title):
    rect = patches.Rectangle((x, y), w, h, linewidth=1.5, edgecolor='#000000', facecolor='#ffffff', zorder=1)
    ax.add_patch(rect)
    ax.text(x + 0.2, y + h - 0.35, "«subsystem»", fontsize=8.5, style='italic', color='#000000')
    ax.text(x + 0.2, y + h - 0.7, title, fontsize=10.5, fontweight='bold', color='#000000')

def draw_ellipse(ax, x, y, w, h, text):
    ellipse = patches.Ellipse((x, y), w, h, facecolor='#ffffff', edgecolor='#000000', lw=1.3, zorder=3)
    ax.add_patch(ellipse)
    ax.text(x, y, text, fontsize=8.5, fontweight='bold', ha='center', va='center', color='#000000', zorder=4)
    return (x, y)

def draw_assoc_line(ax, pt_actor, pt_uc, ew, side='left'):
    ex, ey = pt_uc
    if side == 'left':
        ex_border = ex - (ew / 2)
    else:
        ex_border = ex + (ew / 2)
    ax.plot([pt_actor[0], ex_border], [pt_actor[1], ey], color='#000000', lw=1.1, zorder=2)

def draw_relation(ax, pt_from, pt_to, label="«include»"):
    ax.annotate("", xy=pt_to, xytext=pt_from,
                arrowprops=dict(arrowstyle="->", lw=1.1, linestyle="--", color="#000000"), zorder=3)
    mid_x = (pt_from[0] + pt_to[0]) / 2 + 0.15
    mid_y = (pt_from[1] + pt_to[1]) / 2
    ax.text(mid_x, mid_y, label, fontsize=7.5, style='italic', color='#000000', va='center')


# =============================================================
# 1. OVERALL SYSTEM USE CASE DIAGRAM (B&W)
# =============================================================
def make_overall_uml_bw():
    fig, ax = plt.subplots(figsize=(13, 14), dpi=300)
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 14)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    sys_x = 3.6
    sys_y = 0.5
    sys_w = 6.0
    sys_h = 13.0
    draw_subsystem_box(ax, sys_x, sys_y, sys_w, sys_h, "Trạm Điều Khiển FloodGuard (ESP32)")

    uc_center_x = 6.6
    uc_list = [
        ("UC01: Đọc & tiền xử lý dữ liệu cảm biến", 11.5),
        ("UC02: Đánh giá FSM & xử lý dải trễ", 10.3),
        ("UC03: Tự động điều khiển máy bơm", 9.1),
        ("UC04: Tự động điều khiển van thoát lũ", 7.9),
        ("UC05: Tự động báo động LED & Còi", 6.7),
        ("UC06: Tự động chuyển an toàn về AUTO", 5.5),
        ("UC07: Truyền nhận dữ liệu Telemetry API", 4.3),
        ("UC08: Giám sát trạng thái qua Web", 3.1),
        ("UC09: Chuyển đổi chế độ AUTO/MANUAL", 1.9),
        ("UC10: Can thiệp cưỡng chế thiết bị Web", 0.9)
    ]

    uc_pos = {}
    ew = 4.7
    eh = 0.85
    for name, cy in uc_list:
        pt = draw_ellipse(ax, uc_center_x, cy, ew, eh, name)
        uc_pos[name[:4]] = pt

    # Actors
    draw_stick_figure(ax, 1.6, 11.4, "Môi Trường Nước Lũ\n& Nước Mưa", "«environment»", scale=0.95)
    draw_stick_figure(ax, 1.6, 2.5, "Người Vận Hành\n(Giám Sát Viên)", "«actor»", scale=0.95)

    draw_stick_figure(ax, 11.5, 11.4, "Khối Cảm Biến\n(HC-SR04 & Mưa)", "«peripheral»", scale=0.95)
    draw_stick_figure(ax, 11.5, 7.8, "Khối Chấp Hành\n(Bơm, Van, LED, Còi)", "«peripheral»", scale=0.95)
    draw_stick_figure(ax, 11.5, 3.2, "Trình Duyệt Web\n& Hạ Tầng Wi-Fi", "«system»", scale=0.95)

    # Connections
    draw_assoc_line(ax, (2.2, 11.4), uc_pos['UC01'], ew, 'left')

    draw_assoc_line(ax, (2.2, 2.7), uc_pos['UC08'], ew, 'left')
    draw_assoc_line(ax, (2.2, 2.5), uc_pos['UC09'], ew, 'left')
    draw_assoc_line(ax, (2.2, 2.3), uc_pos['UC10'], ew, 'left')

    draw_assoc_line(ax, (10.9, 11.4), uc_pos['UC01'], ew, 'right')

    draw_assoc_line(ax, (10.9, 8.2), uc_pos['UC03'], ew, 'right')
    draw_assoc_line(ax, (10.9, 7.9), uc_pos['UC04'], ew, 'right')
    draw_assoc_line(ax, (10.9, 7.6), uc_pos['UC05'], ew, 'right')
    draw_assoc_line(ax, (10.9, 7.3), uc_pos['UC10'], ew, 'right')

    draw_assoc_line(ax, (10.9, 3.6), uc_pos['UC06'], ew, 'right')
    draw_assoc_line(ax, (10.9, 3.4), uc_pos['UC07'], ew, 'right')
    draw_assoc_line(ax, (10.9, 3.2), uc_pos['UC08'], ew, 'right')
    draw_assoc_line(ax, (10.9, 3.0), uc_pos['UC09'], ew, 'right')
    draw_assoc_line(ax, (10.9, 2.8), uc_pos['UC10'], ew, 'right')

    # Includes
    draw_relation(ax, (uc_center_x, 11.05), (uc_center_x, 10.7), "«include»")
    draw_relation(ax, (uc_center_x, 9.85), (uc_center_x, 9.55), "«include»")

    save_fig(fig, "uc_overall_diagram.png")


# =============================================================
# 2. UC01: Đọc & Tiền Xử Lý Dữ Liệu Cảm Biến (B&W)
# =============================================================
def make_uc01_bw():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 3.2, 0.5, 6.2, 5.5, "Phân Hệ Thu Thập & Xử Lý Cảm Biến")

    ew = 4.6
    eh = 0.8
    p_main = draw_ellipse(ax, 6.3, 4.6, ew, eh, "UC01: Đọc Dữ Liệu Cảm Biến")
    p_sub1 = draw_ellipse(ax, 6.3, 3.3, ew, eh, "Lọc Trung Vị 3 Mẫu (Median Filter)")
    p_sub2 = draw_ellipse(ax, 6.3, 2.1, ew, eh, "Quy Đổi Mực Nước (50cm-5cm -> %)")
    p_sub3 = draw_ellipse(ax, 6.3, 1.0, ew, eh, "Phân Loại Cấp Mưa (ADC & DO)")

    draw_stick_figure(ax, 1.5, 4.6, "Môi Trường Nước Lũ\n& Nước Mưa", "«environment»")
    draw_stick_figure(ax, 1.5, 1.8, "Khối Cảm Biến\nHC-SR04 & FC-37", "«peripheral»")

    draw_assoc_line(ax, (2.1, 4.6), p_main, ew, 'left')
    draw_assoc_line(ax, (2.1, 1.8), p_main, ew, 'left')

    draw_relation(ax, (6.3, 4.2), (6.3, 3.7), "«include»")
    draw_relation(ax, (6.3, 2.9), (6.3, 2.5), "«include»")
    draw_relation(ax, (6.3, 1.7), (6.3, 1.4), "«include»")

    save_fig(fig, "uc01_sensor_processing.png")


# =============================================================
# 3. UC02: Đánh Giá FSM & Xử Lý Dải Trễ (B&W)
# =============================================================
def make_uc02_bw():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.6, 0.5, 6.8, 5.5, "Phân Hệ Máy Trạng Thái FSM & Hysteresis")

    ew = 4.4
    eh = 0.8
    p_main = draw_ellipse(ax, 6.0, 4.6, ew, eh, "UC02: Đánh Giá Trạng Thái FSM")
    p_norm = draw_ellipse(ax, 6.0, 3.4, ew, eh, "Đánh Giá Ngưỡng NORMAL (≤20%)")
    p_warn = draw_ellipse(ax, 6.0, 2.3, ew, eh, "Đánh Giá Ngưỡng WARNING (21-40%)")
    p_dang = draw_ellipse(ax, 6.0, 1.2, ew, eh, "Dải Trễ Hysteresis (Thoát <40% / <20%)")

    draw_stick_figure(ax, 1.2, 4.6, "Khối Cảm Biến\n(Dữ liệu % & Mưa)", "«input»")
    draw_stick_figure(ax, 1.2, 1.8, "Trình Điều Khiển\nFirmware ESP32", "«timer»")

    draw_assoc_line(ax, (1.8, 4.6), p_main, ew, 'left')
    draw_assoc_line(ax, (1.8, 1.8), p_main, ew, 'left')

    draw_relation(ax, (6.0, 4.2), (6.0, 3.8), "«include»")
    draw_relation(ax, (6.0, 3.0), (6.0, 2.7), "«include»")
    draw_relation(ax, (6.0, 1.9), (6.0, 1.6), "«include»")

    save_fig(fig, "uc02_fsm_hysteresis.png")


# =============================================================
# 4. UC03: Tự Động Điều Khiển Máy Bơm (B&W)
# =============================================================
def make_uc03_bw():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.6, 0.5, 5.2, 5.0, "Phân Hệ Điều Khiển Máy Bơm")

    ew = 4.2
    eh = 0.8
    p_main = draw_ellipse(ax, 5.2, 4.1, ew, eh, "UC03: Tự Động Điều Khiển Bơm")
    p_on   = draw_ellipse(ax, 5.2, 2.7, ew, eh, "Kích Relay Active LOW (Bật Bơm)")
    p_off  = draw_ellipse(ax, 5.2, 1.3, ew, eh, "Ngắt Bằng High-Z INPUT (Triệt Rò)")

    draw_stick_figure(ax, 1.1, 4.1, "Máy Trạng Thái\nFSM Controller", "«internal»")
    draw_stick_figure(ax, 8.9, 4.1, "Module Relay 5V\n& Máy Bơm Mini", "«actuator»")

    draw_assoc_line(ax, (1.7, 4.1), p_main, ew, 'left')
    draw_assoc_line(ax, (8.3, 4.1), p_main, ew, 'right')

    draw_relation(ax, (5.2, 3.7), (5.2, 3.1), "«include»")
    draw_relation(ax, (5.2, 2.3), (5.2, 1.7), "«include»")

    save_fig(fig, "uc03_pump_control.png")


# =============================================================
# 5. UC04: Tự Động Điều Khiển Van Thoát Lũ (B&W)
# =============================================================
def make_uc04_bw():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.6, 0.5, 5.2, 5.0, "Phân Hệ Điều Khiển Van Thoát Lũ")

    ew = 4.2
    eh = 0.8
    p_main = draw_ellipse(ax, 5.2, 4.1, ew, eh, "UC04: Tự Động Điều Khiển Van")
    p_mid  = draw_ellipse(ax, 5.2, 2.7, ew, eh, "Mở Xả 50% Góc 90° (Mức DANGER)")
    p_full = draw_ellipse(ax, 5.2, 1.3, ew, eh, "Mở Xả 100% Góc 180° (CRITICAL)")

    draw_stick_figure(ax, 1.1, 4.1, "Máy Trạng Thái\nFSM Controller", "«internal»")
    draw_stick_figure(ax, 8.9, 4.1, "Động Cơ Servo\nSG90 (GPIO 27)", "«actuator»")

    draw_assoc_line(ax, (1.7, 4.1), p_main, ew, 'left')
    draw_assoc_line(ax, (8.3, 4.1), p_main, ew, 'right')

    draw_relation(ax, (5.2, 3.7), (5.2, 3.1), "«include»")
    draw_relation(ax, (5.2, 2.3), (5.2, 1.7), "«include»")

    save_fig(fig, "uc04_valve_control.png")


# =============================================================
# 6. UC05: Cảnh Báo LED & Còi Buzzer (B&W)
# =============================================================
def make_uc05_bw():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.6, 0.5, 5.2, 5.0, "Phân Hệ Báo Động Tại Chỗ")

    ew = 4.2
    eh = 0.8
    p_main = draw_ellipse(ax, 5.2, 4.1, ew, eh, "UC05: Báo Động Tại Chỗ (LED & Còi)")
    p_led  = draw_ellipse(ax, 5.2, 2.7, ew, eh, "Chỉ Thị LED Đa Màu (Xanh/Vàng/Đỏ)")
    p_buz  = draw_ellipse(ax, 5.2, 1.3, ew, eh, "Phát Còi Non-blocking (millis)")

    draw_stick_figure(ax, 1.1, 4.1, "Máy Trạng Thái\nFSM Controller", "«internal»")
    draw_stick_figure(ax, 8.9, 4.1, "Cụm 3 LED & Còi\nBuzzer 5V", "«signaling»")

    draw_assoc_line(ax, (1.7, 4.1), p_main, ew, 'left')
    draw_assoc_line(ax, (8.3, 4.1), p_main, ew, 'right')

    draw_relation(ax, (5.2, 3.7), (5.2, 3.1), "«include»")
    draw_relation(ax, (5.2, 2.3), (5.2, 1.7), "«include»")

    save_fig(fig, "uc05_signaling_buzzer_led.png")


# =============================================================
# 7. UC06: Failsafe to AUTO (B&W)
# =============================================================
def make_uc06_bw():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.6, 0.5, 5.2, 5.0, "Phân Hệ An Toàn Tự Động (Failsafe)")

    ew = 4.2
    eh = 0.8
    p_main = draw_ellipse(ax, 5.2, 4.1, ew, eh, "UC06: Failsafe to AUTO Mode")
    p_loss = draw_ellipse(ax, 5.2, 2.7, ew, eh, "Giám Sát Timeout Kết Nối Wi-Fi")
    p_auto = draw_ellipse(ax, 5.2, 1.3, ew, eh, "Cưỡng Chế Chuyển Về AUTO")

    draw_stick_figure(ax, 1.1, 4.1, "Bộ Giám Sát Mạng\nWatchdog ESP32", "«system»")
    draw_stick_figure(ax, 8.9, 4.1, "Máy Trạng Thái\nFSM Controller", "«internal»")

    draw_assoc_line(ax, (1.7, 4.1), p_main, ew, 'left')
    draw_assoc_line(ax, (8.3, 4.1), p_main, ew, 'right')

    draw_relation(ax, (5.2, 3.7), (5.2, 3.1), "«include»")
    draw_relation(ax, (5.2, 2.3), (5.2, 1.7), "«include»")

    save_fig(fig, "uc06_network_failsafe.png")


# =============================================================
# 8. UC07: Truyền Nhận Telemetry & API (B&W)
# =============================================================
def make_uc07_bw():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.6, 0.5, 5.2, 5.0, "Phân Hệ Web Server & REST API")

    ew = 4.2
    eh = 0.8
    p_main = draw_ellipse(ax, 5.2, 4.1, ew, eh, "UC07: Truyền Nhận Telemetry & API")
    p_get  = draw_ellipse(ax, 5.2, 2.7, ew, eh, "Đóng Gói JSON (GET /api/status)")
    p_post = draw_ellipse(ax, 5.2, 1.3, ew, eh, "Nhận Lệnh Điều Khiển (/api/control)")

    draw_stick_figure(ax, 1.1, 4.1, "Trình Duyệt Web\nClient (Browser)", "«client»")
    draw_stick_figure(ax, 8.9, 4.1, "ESP32 Firmware\nWeb Server Port 80", "«server»")

    draw_assoc_line(ax, (1.7, 4.1), p_main, ew, 'left')
    draw_assoc_line(ax, (8.3, 4.1), p_main, ew, 'right')

    draw_relation(ax, (5.2, 3.7), (5.2, 3.1), "«include»")
    draw_relation(ax, (5.2, 2.3), (5.2, 1.7), "«include»")

    save_fig(fig, "uc07_telemetry_api.png")


# =============================================================
# 9. UC08: Giám Sát Web Dashboard (B&W)
# =============================================================
def make_uc08_bw():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.6, 0.5, 5.2, 5.0, "Phân Hệ Web Dashboard Giám Sát")

    ew = 4.2
    eh = 0.8
    p_main = draw_ellipse(ax, 5.2, 4.1, ew, eh, "UC08: Giám Sát Trạng Thái Web")
    p_card = draw_ellipse(ax, 5.2, 2.7, ew, eh, "Hiển Thị Thanh Đo Mực Nước %")
    p_st   = draw_ellipse(ax, 5.2, 1.3, ew, eh, "Cập Nhật Trạng Thái Bơm / Van / Còi")

    draw_stick_figure(ax, 1.1, 4.1, "Người Vận Hành\n(Giám Sát Viên)", "«actor»")
    draw_stick_figure(ax, 8.9, 4.1, "Web Dashboard\n(HTML/CSS/JS SPA)", "«interface»")

    draw_assoc_line(ax, (1.7, 4.1), p_main, ew, 'left')
    draw_assoc_line(ax, (8.3, 4.1), p_main, ew, 'right')

    draw_relation(ax, (5.2, 3.7), (5.2, 3.1), "«include»")
    draw_relation(ax, (5.2, 2.3), (5.2, 1.7), "«include»")

    save_fig(fig, "uc08_web_dashboard.png")


# =============================================================
# 10. UC09: Chuyển Đổi AUTO/MANUAL (B&W)
# =============================================================
def make_uc09_bw():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.6, 0.5, 5.2, 5.0, "Phân Hệ Quản Lý Chế Độ Vận Hành")

    ew = 4.2
    eh = 0.8
    p_main = draw_ellipse(ax, 5.2, 4.1, ew, eh, "UC09: Chuyển Đổi Chế Độ Vận Hành")
    p_auto = draw_ellipse(ax, 5.2, 2.7, ew, eh, "Khóa Phím Web, Bật Chế Độ AUTO")
    p_manu = draw_ellipse(ax, 5.2, 1.3, ew, eh, "Mở Khóa Nút, Bật Chế Độ MANUAL")

    draw_stick_figure(ax, 1.1, 4.1, "Người Vận Hành\n(Giám Sát Viên)", "«actor»")
    draw_stick_figure(ax, 8.9, 4.1, "ESP32 Controller\n(Cờ isAutoMode)", "«controller»")

    draw_assoc_line(ax, (1.7, 4.1), p_main, ew, 'left')
    draw_assoc_line(ax, (8.3, 4.1), p_main, ew, 'right')

    draw_relation(ax, (5.2, 3.7), (5.2, 3.1), "«extend»")
    draw_relation(ax, (5.2, 2.3), (5.2, 1.7), "«extend»")

    save_fig(fig, "uc09_mode_switch.png")


# =============================================================
# 11. UC10: Can Thiệp Cưỡng Chế Thiết Bị (B&W)
# =============================================================
def make_uc10_bw():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.6, 0.5, 5.2, 5.0, "Phân Hệ Can Thiệp Cưỡng Chế Thiết Bị")

    ew = 4.2
    eh = 0.8
    p_main = draw_ellipse(ax, 5.2, 4.1, ew, eh, "UC10: Can Thiệp Cưỡng Chế Web")
    p_pump = draw_ellipse(ax, 5.2, 2.7, ew, eh, "Bật / Tắt Bơm Thủ Công")
    p_gate = draw_ellipse(ax, 5.2, 1.3, ew, eh, "Chọn Góc Mở Van 0° / 50% / 100%")

    draw_stick_figure(ax, 1.1, 4.1, "Người Vận Hành\n(Giám Sát Viên)", "«actor»")
    draw_stick_figure(ax, 8.9, 4.1, "Relay Bơm &\nServo SG90 Van", "«actuator»")

    draw_assoc_line(ax, (1.7, 4.1), p_main, ew, 'left')
    draw_assoc_line(ax, (8.3, 4.1), p_main, ew, 'right')

    draw_relation(ax, (5.2, 3.7), (5.2, 3.1), "«extend»")
    draw_relation(ax, (5.2, 2.3), (5.2, 1.7), "«extend»")

    save_fig(fig, "uc10_manual_override.png")


if __name__ == "__main__":
    print("Generating pure black & white UML Use Case diagrams...")
    make_overall_uml_bw()
    make_uc01_bw()
    make_uc02_bw()
    make_uc03_bw()
    make_uc04_bw()
    make_uc05_bw()
    make_uc06_bw()
    make_uc07_bw()
    make_uc08_bw()
    make_uc09_bw()
    make_uc10_bw()
    print("All 11 pure black & white UML diagrams generated successfully!")
