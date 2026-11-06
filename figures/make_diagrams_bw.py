import matplotlib.pyplot as plt
import matplotlib.patches as patches
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
    print(f"Generated B&W (Strict UML Actors): {filename}")

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
    ax.text(x, y - 0.85 * scale, label, fontsize=8.5, fontweight='bold', ha='center', va='top', color='#000000')
    if sublabel:
        ax.text(x, y - 1.18 * scale, sublabel, fontsize=7.5, style='italic', ha='center', va='top', color='#333333')

def draw_subsystem_box(ax, x, y, w, h, title):
    rect = patches.Rectangle((x, y), w, h, linewidth=1.5, edgecolor='#000000', facecolor='#ffffff', zorder=1)
    ax.add_patch(rect)
    ax.text(x + 0.2, y + h - 0.35, "«subsystem»", fontsize=8.5, style='italic', color='#000000')
    ax.text(x + 0.2, y + h - 0.7, title, fontsize=10.0, fontweight='bold', color='#000000')

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
# 1. OVERALL SYSTEM USE CASE DIAGRAM (Strict UML Actors)
# Actors: ONLY Environmental & Human actors
# Internal Subsystem: Contains ESP32, Sensors, Actuators, Signaling
# =============================================================
def make_overall_uml_bw():
    fig, ax = plt.subplots(figsize=(15.5, 14.5), dpi=300)
    ax.set_xlim(0, 15.5)
    ax.set_ylim(0, 14.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Subsystem box: contains ESP32 controller and all onboard peripherals
    sys_x = 3.6
    sys_y = 0.5
    sys_w = 7.8
    sys_h = 13.5
    draw_subsystem_box(ax, sys_x, sys_y, sys_w, sys_h, 
                       "Hệ Thống FloodGuard (ESP32, Cảm Biến & Thiết Bị Chấp Hành)")

    uc_center_x = 7.5
    uc_list = [
        ("UC01: Đọc & Tiền Xử Lý Dữ Liệu Cảm Biến", 12.0),
        ("UC02: Tự Động Đánh Giá FSM & Dải Trễ", 10.8),
        ("UC03: Tự Động Điều Khiển Máy Bơm", 9.6),
        ("UC04: Tự Động Điều Khiển Van Thoát Lũ", 8.4),
        ("UC05: Báo Động Tại Chỗ (LED & Còi)", 7.2),
        ("UC06: Tự Động Chuyển An Toàn (Failsafe)", 6.0),
        ("UC07: Truyền Nhận Dữ Liệu Web Telemetry & API", 4.8),
        ("UC08: Giám Sát Trạng Thái Trạm Qua Web", 3.6),
        ("UC09: Chuyển Đổi Chế Độ (AUTO / MANUAL)", 2.4),
        ("UC10: Can Thiệp Cưỡng Chế Thiết Bị Từ Web", 1.2)
    ]

    uc_pos = {}
    ew = 5.6
    eh = 0.85
    for name, cy in uc_list:
        pt = draw_ellipse(ax, uc_center_x, cy, ew, eh, name)
        uc_pos[name[:4]] = pt

    # LEFT SIDE ACTORS: STRICTLY ENVIRONMENTAL & HUMAN
    # 1. Water Surface / Flood Water
    draw_stick_figure(ax, 1.4, 12.0, "Mặt Nước Hồ Thu\n(Mực Nước Lũ)", "«environmental actor»", scale=0.9)
    draw_assoc_line(ax, (2.2, 12.0), uc_pos['UC01'], ew, 'left')
    draw_assoc_line(ax, (2.2, 11.7), uc_pos['UC03'], ew, 'left')
    draw_assoc_line(ax, (2.2, 11.4), uc_pos['UC04'], ew, 'left')

    # 2. Rainfall / Weather
    draw_stick_figure(ax, 1.4, 8.5, "Hiện Tượng Mưa Rơi\n(Nước Mưa Vật Lý)", "«environmental actor»", scale=0.9)
    draw_assoc_line(ax, (2.2, 8.7), uc_pos['UC01'], ew, 'left')

    # RIGHT SIDE ACTORS: STRICTLY HUMAN & RESIDENTS
    # 3. Local Residents receiving alert
    draw_stick_figure(ax, 13.8, 7.2, "Người Dân Quanh Trạm\n& Kỹ Thuật Viên Tại Chỗ", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (12.7, 7.2), uc_pos['UC05'], ew, 'right')

    # 4. Remote Supervisor / Operator
    draw_stick_figure(ax, 13.8, 3.2, "Người Vận Hành\n(Giám Sát Viên Từ Xa)", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (12.7, 4.4), uc_pos['UC07'], ew, 'right')
    draw_assoc_line(ax, (12.7, 3.6), uc_pos['UC08'], ew, 'right')
    draw_assoc_line(ax, (12.7, 2.8), uc_pos['UC09'], ew, 'right')
    draw_assoc_line(ax, (12.7, 2.0), uc_pos['UC10'], ew, 'right')
    draw_assoc_line(ax, (12.7, 4.8), uc_pos['UC06'], ew, 'right')

    # Internal relationships
    draw_relation(ax, (uc_center_x, 11.55), (uc_center_x, 11.25), "«include»")
    draw_relation(ax, (uc_center_x, 10.35), (uc_center_x, 10.05), "«include»")

    save_fig(fig, "uc_overall_diagram.png")


# =============================================================
# 2. UC01: Đọc & Tiền Xử Lý Dữ Liệu Cảm Biến
# =============================================================
def make_uc01_bw():
    fig, ax = plt.subplots(figsize=(11.5, 7.2), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 7.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # System boundary includes sensors and processing
    draw_subsystem_box(ax, 3.8, 0.5, 7.2, 6.2, 
                       "Phân Hệ Đo Đạc & Cảm Biến (HC-SR04 & Mưa trên ESP32)")

    ew = 5.2
    eh = 0.82
    p_main = draw_ellipse(ax, 7.4, 5.2, ew, eh, "UC01: Đọc & Tiền Xử Lý Dữ Liệu")
    p_sub1 = draw_ellipse(ax, 7.4, 3.8, ew, eh, "Kích Phát & Thu Siêu Âm HC-SR04")
    p_sub2 = draw_ellipse(ax, 7.4, 2.4, ew, eh, "Lọc Trung Vị 3 Mẫu & Quy Đổi Mực Nước %")
    p_sub3 = draw_ellipse(ax, 7.4, 1.0, ew, eh, "Đo Điện Trở Nước Mưa & Phân Tầng ADC")

    # Actors: ONLY Environmental Stimuli
    draw_stick_figure(ax, 1.5, 5.2, "Mặt Nước Hồ Thu\n(Mực Nước Dâng/Rút)", "«environmental actor»", scale=0.9)
    draw_stick_figure(ax, 1.5, 1.8, "Hạt Mưa Rơi &\nNước Đọng", "«environmental actor»", scale=0.9)

    # Connections to UC01
    draw_assoc_line(ax, (2.3, 5.2), p_main, ew, 'left')
    ax.text(3.05, 5.4, "Phản xạ sóng\nsiêu âm 40kHz", fontsize=7.5, style='italic', ha='center', color='#000000')

    draw_assoc_line(ax, (2.3, 1.8), p_main, ew, 'left')
    ax.text(3.05, 2.5, "Dẫn điện qua\nbản cực cảm biến", fontsize=7.5, style='italic', ha='center', color='#000000')

    # Includes inside subsystem
    draw_relation(ax, (7.4, 4.75), (7.4, 4.25), "«include»")
    draw_relation(ax, (7.4, 3.35), (7.4, 2.85), "«include»")
    draw_relation(ax, (7.4, 1.95), (7.4, 1.45), "«include»")

    save_fig(fig, "uc01_sensor_processing.png")


# =============================================================
# 3. UC02: Đánh Giá FSM & Xử Lý Dải Trễ (B&W)
# =============================================================
def make_uc02_bw():
    fig, ax = plt.subplots(figsize=(10.5, 6.5), dpi=300)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 6.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 3.4, 0.5, 6.6, 5.5, 
                       "Phân Hệ Logic Điều Khiển FSM & Dải Trễ (ESP32)")

    ew = 5.0
    eh = 0.8
    p_main = draw_ellipse(ax, 6.7, 4.6, ew, eh, "UC02: Đánh Giá Trạng Thái FSM & Hysteresis")
    p_norm = draw_ellipse(ax, 6.7, 3.4, ew, eh, "Đánh Giá Ngưỡng NORMAL / WARNING")
    p_dang = draw_ellipse(ax, 6.7, 2.3, ew, eh, "Đánh Giá Ngưỡng DANGER / CRITICAL")
    p_hyst = draw_ellipse(ax, 6.7, 1.2, ew, eh, "Xử Lý Dải Trễ Chống Rung (Thoát <40% / <20%)")

    # Environmental Actor represents physical flood variation
    draw_stick_figure(ax, 1.4, 3.5, "Môi Trường Mưa Lũ\n(Biến Thiên Mực Nước)", "«environmental actor»", scale=0.9)

    draw_assoc_line(ax, (2.2, 3.5), p_main, ew, 'left')
    ax.text(2.8, 4.3, "Mặt nước dập dềnh\nquanh biên ngưỡng", fontsize=7.5, style='italic', ha='center', color='#000000')

    draw_relation(ax, (6.7, 4.15), (6.7, 3.85), "«include»")
    draw_relation(ax, (6.7, 2.95), (6.7, 2.75), "«include»")
    draw_relation(ax, (6.7, 1.85), (6.7, 1.65), "«include»")

    save_fig(fig, "uc02_fsm_hysteresis.png")


# =============================================================
# 4. UC03: Tự Động Điều Khiển Máy Bơm
# =============================================================
def make_uc03_bw():
    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 1.0, 0.5, 6.6, 5.2, 
                       "Phân Hệ Bơm Thoát Nước (ESP32, Relay & Máy Bơm Mini)")

    ew = 5.0
    eh = 0.8
    p_main = draw_ellipse(ax, 4.3, 4.2, ew, eh, "UC03: Tự Động Điều Khiển Máy Bơm")
    p_on   = draw_ellipse(ax, 4.3, 2.7, ew, eh, "Kích Relay Active LOW (Bật Bơm Khi DANGER)")
    p_off  = draw_ellipse(ax, 4.3, 1.2, ew, eh, "Ngắt Bằng Trở Kháng Cao High-Z (INPUT)")

    # Right Actor: The water volume being evacuated
    draw_stick_figure(ax, 9.8, 3.5, "Khối Nước Cần\nTiêu Thoát Khỏi Hồ", "«environmental actor»", scale=0.9)

    draw_assoc_line(ax, (9.0, 3.5), p_main, ew, 'right')
    ax.text(7.7, 4.3, "Hút và tiêu xả\ndòng nước ngập", fontsize=7.5, style='italic', ha='center', color='#000000')

    draw_relation(ax, (4.3, 3.75), (4.3, 3.15), "«include»")
    draw_relation(ax, (4.3, 2.25), (4.3, 1.65), "«include»")

    save_fig(fig, "uc03_pump_control.png")


# =============================================================
# 5. UC04: Tự Động Điều Khiển Van Thoát Lũ
# =============================================================
def make_uc04_bw():
    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 1.0, 0.5, 6.6, 5.2, 
                       "Phân Hệ Cửa Van Thoát Lũ (ESP32, PWM & Động Cơ Servo SG90)")

    ew = 5.0
    eh = 0.8
    p_main = draw_ellipse(ax, 4.3, 4.2, ew, eh, "UC04: Tự Động Điều Khiển Van Thoát Lũ")
    p_mid  = draw_ellipse(ax, 4.3, 2.7, ew, eh, "Xuất PWM Mở Van 50% Góc 90° (DANGER)")
    p_full = draw_ellipse(ax, 4.3, 1.2, ew, eh, "Xuất PWM Mở Van 100% Góc 180° (CRITICAL)")

    # Right Actor: River / drainage flow being released
    draw_stick_figure(ax, 9.8, 3.5, "Dòng Chảy Xả Lũ\n& Hồ Chứa Nước", "«environmental actor»", scale=0.9)

    draw_assoc_line(ax, (9.0, 3.5), p_main, ew, 'right')
    ax.text(7.7, 4.3, "Điều tiết lưu lượng\ndòng xả cống lũ", fontsize=7.5, style='italic', ha='center', color='#000000')

    draw_relation(ax, (4.3, 3.75), (4.3, 3.15), "«include»")
    draw_relation(ax, (4.3, 2.25), (4.3, 1.65), "«include»")

    save_fig(fig, "uc04_valve_control.png")


# =============================================================
# 6. UC05: Cảnh Báo LED & Còi Buzzer
# =============================================================
def make_uc05_bw():
    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 1.0, 0.5, 6.6, 5.2, 
                       "Phân Hệ Báo Động Tại Chỗ (ESP32, Cụm 3 LED & Còi Buzzer)")

    ew = 5.0
    eh = 0.8
    p_main = draw_ellipse(ax, 4.3, 4.2, ew, eh, "UC05: Báo Động Tại Chỗ (LED & Còi)")
    p_led  = draw_ellipse(ax, 4.3, 2.7, ew, eh, "Chỉ Thị Trực Quan LED (Xanh/Vàng/Đỏ)")
    p_buz  = draw_ellipse(ax, 4.3, 1.2, ew, eh, "Kích Còi Báo Động Non-blocking (millis)")

    # Right Actor: Human residents receiving light/sound signals
    draw_stick_figure(ax, 9.8, 3.5, "Người Dân Quanh Trạm\n& Cán Bộ Thực Địa", "«human actor»", scale=0.9)

    draw_assoc_line(ax, (9.0, 3.5), p_main, ew, 'right')
    ax.text(7.7, 4.3, "Tiếp nhận âm thanh hú\n& ánh sáng chỉ thị", fontsize=7.5, style='italic', ha='center', color='#000000')

    draw_relation(ax, (4.3, 3.75), (4.3, 3.15), "«include»")
    draw_relation(ax, (4.3, 2.25), (4.3, 1.65), "«include»")

    save_fig(fig, "uc05_signaling_buzzer_led.png")


# =============================================================
# 7. UC06: Failsafe to AUTO
# =============================================================
def make_uc06_bw():
    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 3.4, 0.5, 7.2, 5.2, 
                       "Phân Hệ Giám Sát Tự Trị An Toàn (ESP32 Failsafe)")

    ew = 5.2
    eh = 0.8
    p_main = draw_ellipse(ax, 7.0, 4.2, ew, eh, "UC06: Tự Động Chuyển An Toàn Về AUTO")
    p_loss = draw_ellipse(ax, 7.0, 2.7, ew, eh, "Giám Sát Mất Heartbeat / Ngắt Mạng Wi-Fi")
    p_auto = draw_ellipse(ax, 7.0, 1.2, ew, eh, "Cưỡng Chế Chuyển Quyền Vận Hành Về AUTO")

    # Actor: Human operator whose connection was lost
    draw_stick_figure(ax, 1.4, 3.5, "Người Vận Hành\n(Mất Kết Nối / Quên Khóa)", "«human actor»", scale=0.9)

    draw_assoc_line(ax, (2.2, 3.5), p_main, ew, 'left')
    ax.text(2.8, 4.3, "Mất kết nối mạng\nquá thời gian timeout", fontsize=7.5, style='italic', ha='center', color='#000000')

    draw_relation(ax, (7.0, 3.75), (7.0, 3.15), "«include»")
    draw_relation(ax, (7.0, 2.25), (7.0, 1.65), "«include»")

    save_fig(fig, "uc06_network_failsafe.png")


# =============================================================
# 8. UC07: Truyền Nhận Telemetry & API
# =============================================================
def make_uc07_bw():
    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 1.0, 0.5, 6.8, 5.2, 
                       "Phân Hệ Web Server & REST API Cục Bộ (ESP32 Port 80)")

    ew = 5.2
    eh = 0.8
    p_main = draw_ellipse(ax, 4.4, 4.2, ew, eh, "UC07: Truyền Nhận Web Telemetry & API")
    p_get  = draw_ellipse(ax, 4.4, 2.7, ew, eh, "Đóng Gói Chuỗi JSON (GET /api/status)")
    p_post = draw_ellipse(ax, 4.4, 1.2, ew, eh, "Tiếp Nhận Gói Lệnh Điều Khiển (/api/control)")

    # Right Actor: Remote supervisor interacting via HTTP
    draw_stick_figure(ax, 9.8, 3.5, "Người Vận Hành\n(Giám Sát Viên Từ Xa)", "«human actor»", scale=0.9)

    draw_assoc_line(ax, (9.0, 3.5), p_main, ew, 'right')
    ax.text(7.8, 4.3, "Gửi HTTP Request\n& nhận dữ liệu JSON", fontsize=7.5, style='italic', ha='center', color='#000000')

    draw_relation(ax, (4.4, 3.75), (4.4, 3.15), "«include»")
    draw_relation(ax, (4.4, 2.25), (4.4, 1.65), "«include»")

    save_fig(fig, "uc07_telemetry_api.png")


# =============================================================
# 9. UC08: Giám Sát Web Dashboard
# =============================================================
def make_uc08_bw():
    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 3.6, 0.5, 7.0, 5.2, 
                       "Phân Hệ Web Dashboard Giám Sát (Giao Diện Trực Quan SPA)")

    ew = 5.2
    eh = 0.8
    p_main = draw_ellipse(ax, 7.1, 4.2, ew, eh, "UC08: Giám Sát Trạng Thái Trạm Qua Web")
    p_card = draw_ellipse(ax, 7.1, 2.7, ew, eh, "Cập Nhật Thanh Đo Mực Nước % & Cấp Mưa")
    p_st   = draw_ellipse(ax, 7.1, 1.2, ew, eh, "Hiển Thị Trạng Thái Bơm, Van Xả & Báo Động")

    draw_stick_figure(ax, 1.4, 3.5, "Người Vận Hành\n(Giám Sát Viên)", "«human actor»", scale=0.9)

    draw_assoc_line(ax, (2.2, 3.5), p_main, ew, 'left')
    ax.text(2.9, 4.3, "Theo dõi thông số\ntrên trình duyệt Web", fontsize=7.5, style='italic', ha='center', color='#000000')

    draw_relation(ax, (7.1, 3.75), (7.1, 3.15), "«include»")
    draw_relation(ax, (7.1, 2.25), (7.1, 1.65), "«include»")

    save_fig(fig, "uc08_web_dashboard.png")


# =============================================================
# 10. UC09: Chuyển Đổi AUTO/MANUAL
# =============================================================
def make_uc09_bw():
    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 3.6, 0.5, 7.0, 5.2, 
                       "Phân Hệ Quản Lý Chế Độ Vận Hành (ESP32 Controller)")

    ew = 5.2
    eh = 0.8
    p_main = draw_ellipse(ax, 7.1, 4.2, ew, eh, "UC09: Chuyển Đổi Chế Độ (AUTO / MANUAL)")
    p_auto = draw_ellipse(ax, 7.1, 2.7, ew, eh, "Khóa Phím Web, Giao Quyền Tự Động Cho FSM")
    p_manu = draw_ellipse(ax, 7.1, 1.2, ew, eh, "Mở Khóa Nút Bấm, Cho Phép Can Thiệp Thủ Công")

    draw_stick_figure(ax, 1.4, 3.5, "Người Vận Hành\n(Giám Sát Viên)", "«human actor»", scale=0.9)

    draw_assoc_line(ax, (2.2, 3.5), p_main, ew, 'left')
    ax.text(2.9, 4.3, "Nhấn nút gạt đổi mode\ntrên Dashboard Web", fontsize=7.5, style='italic', ha='center', color='#000000')

    draw_relation(ax, (7.1, 3.75), (7.1, 3.15), "«extend»")
    draw_relation(ax, (7.1, 2.25), (7.1, 1.65), "«extend»")

    save_fig(fig, "uc09_mode_switch.png")


# =============================================================
# 11. UC10: Can Thiệp Cưỡng Chế Thiết Bị
# =============================================================
def make_uc10_bw():
    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 1.0, 0.5, 6.8, 5.2, 
                       "Phân Hệ Can Thiệp Cưỡng Chế Thiết Bị (Bơm & Van Xả)")

    ew = 5.2
    eh = 0.8
    p_main = draw_ellipse(ax, 4.4, 4.2, ew, eh, "UC10: Can Thiệp Cưỡng Chế Thiết Bị Từ Web")
    p_pump = draw_ellipse(ax, 4.4, 2.7, ew, eh, "Bật / Tắt Bơm Thủ Công Qua Kỹ Thuật High-Z")
    p_gate = draw_ellipse(ax, 4.4, 1.2, ew, eh, "Điều Khiển Góc Van Xả Lũ (0° / 90° / 180°)")

    # Left Actor: Operator commanding
    draw_stick_figure(ax, 9.8, 4.2, "Người Vận Hành\n(Giám Sát Viên)", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (9.0, 4.2), p_main, ew, 'right')
    ax.text(7.9, 4.8, "Nhấn phím cưỡng chế\nbơm / mở van xả", fontsize=7.5, style='italic', ha='center', color='#000000')

    # Right Actor: Water volume impacted by override command
    draw_stick_figure(ax, 9.8, 1.6, "Khối Nước Hồ Thu\n& Cửa Cống Lũ", "«environmental actor»", scale=0.9)
    draw_assoc_line(ax, (9.0, 1.6), p_main, ew, 'right')
    ax.text(7.9, 2.2, "Bơm hút / xả nước\ntheo lệnh cưỡng chế", fontsize=7.5, style='italic', ha='center', color='#000000')

    draw_relation(ax, (4.4, 3.75), (4.4, 3.15), "«extend»")
    draw_relation(ax, (4.4, 2.25), (4.4, 1.65), "«extend»")

    save_fig(fig, "uc10_manual_override.png")


if __name__ == "__main__":
    print("Generating pure black & white UML Use Case diagrams with strict UML Actors...")
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
    print("All 11 strict UML diagrams generated successfully!")
