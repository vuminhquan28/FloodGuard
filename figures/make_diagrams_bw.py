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
    ax.text(x, y - 0.85 * scale, label, fontsize=8.5, fontweight='bold', ha='center', va='top', color='#000000')
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
# 1. OVERALL SYSTEM USE CASE DIAGRAM (B&W) - ENHANCED INTERACTION
# =============================================================
def make_overall_uml_bw():
    fig, ax = plt.subplots(figsize=(14.5, 14.5), dpi=300)
    ax.set_xlim(0, 14.5)
    ax.set_ylim(0, 14.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    sys_x = 4.3
    sys_y = 0.5
    sys_w = 6.0
    sys_h = 13.5
    draw_subsystem_box(ax, sys_x, sys_y, sys_w, sys_h, "Trạm Điều Khiển FloodGuard (ESP32)")

    uc_center_x = 7.3
    uc_list = [
        ("UC01: Đọc & tiền xử lý dữ liệu cảm biến", 12.0),
        ("UC02: Đánh giá FSM & xử lý dải trễ", 10.8),
        ("UC03: Tự động điều khiển máy bơm", 9.6),
        ("UC04: Tự động điều khiển van thoát lũ", 8.4),
        ("UC05: Tự động báo động LED & Còi", 7.2),
        ("UC06: Tự động chuyển an toàn về AUTO", 6.0),
        ("UC07: Truyền nhận dữ liệu Telemetry API", 4.8),
        ("UC08: Giám sát trạng thái qua Web", 3.6),
        ("UC09: Chuyển đổi chế độ AUTO/MANUAL", 2.4),
        ("UC10: Can thiệp cưỡng chế thiết bị Web", 1.2)
    ]

    uc_pos = {}
    ew = 4.7
    eh = 0.85
    for name, cy in uc_list:
        pt = draw_ellipse(ax, uc_center_x, cy, ew, eh, name)
        uc_pos[name[:4]] = pt

    # LEFT SIDE ACTORS:
    # 1. Environmental Actor (top-left)
    draw_stick_figure(ax, 1.4, 13.0, "Môi Trường Nước Lũ\n& Nước Mưa", "«environmental actor»", scale=0.9)
    
    # 2. Sensor Peripheral Actor (middle-left, positioned between Environment and UC01)
    draw_stick_figure(ax, 1.4, 10.0, "Khối Cảm Biến\n(HC-SR04 & Mưa)", "«sensor peripheral»", scale=0.9)

    # DIRECT INTERACTION ARROW: Environmental Stimulus -> Sensors
    ax.annotate("", xy=(1.4, 10.8), xytext=(1.4, 11.9),
                arrowprops=dict(arrowstyle="->", lw=1.3, linestyle="-", color="#000000"), zorder=5)
    ax.text(1.5, 11.35, "Tác động vật lý:\n• Phản xạ sóng siêu âm 40kHz\n• Nước mưa đọng làm giảm trở", 
            fontsize=7.5, style='italic', color='#000000', va='center')

    # DIRECT INTERACTION LINE: Sensors -> UC01
    draw_assoc_line(ax, (2.2, 10.0), uc_pos['UC01'], ew, 'left')
    ax.text(3.1, 10.9, "Tín hiệu điện:\nXung Echo (D12)\n& ADC (D35)", fontsize=7.5, style='italic', color='#000000', ha='center')

    # 3. Human Operator (bottom left)
    draw_stick_figure(ax, 1.4, 2.5, "Người Vận Hành\n(Giám Sát Viên)", "«human actor»", scale=0.9)

    # Operator interacts with Web System (drawn at bottom right or connected to UC08, UC09, UC10)
    draw_assoc_line(ax, (2.1, 2.7), uc_pos['UC08'], ew, 'left')
    draw_assoc_line(ax, (2.1, 2.5), uc_pos['UC09'], ew, 'left')
    draw_assoc_line(ax, (2.1, 2.3), uc_pos['UC10'], ew, 'left')

    # RIGHT SIDE ACTORS:
    # 4. Actuator Subsystem (mid right)
    draw_stick_figure(ax, 13.0, 8.4, "Khối Chấp Hành\n(Bơm, Van, LED, Còi)", "«actuator peripheral»", scale=0.9)

    # 5. Physical Environment / Residents receiving Actuator Impact
    draw_stick_figure(ax, 13.0, 11.8, "Khu Vực Tiêu Thoát\n& Dân Cư Quanh Trạm", "«affected environment»", scale=0.9)

    # DIRECT INTERACTION ARROW: Actuators -> Affected Environment / People
    ax.annotate("", xy=(13.0, 11.0), xytext=(13.0, 9.4),
                arrowprops=dict(arrowstyle="->", lw=1.3, linestyle="-", color="#000000"), zorder=5)
    ax.text(13.1, 10.2, "Tác động thực tế:\n• Bơm hút xả dòng chảy\n• Mở van thoát lũ\n• Phát âm thanh cảnh báo", 
            fontsize=7.5, style='italic', color='#000000', va='center')

    # 6. Web Client / Network (bottom right)
    draw_stick_figure(ax, 13.0, 3.8, "Trình Duyệt Web\n& Hạ Tầng Wi-Fi", "«network system»", scale=0.9)

    # Connections to Actuators (UC03, UC04, UC05, UC10)
    draw_assoc_line(ax, (12.3, 8.8), uc_pos['UC03'], ew, 'right')
    draw_assoc_line(ax, (12.3, 8.5), uc_pos['UC04'], ew, 'right')
    draw_assoc_line(ax, (12.3, 8.2), uc_pos['UC05'], ew, 'right')
    draw_assoc_line(ax, (12.3, 7.9), uc_pos['UC10'], ew, 'right')

    # Connections to Web Client (UC06, UC07, UC08, UC09, UC10)
    draw_assoc_line(ax, (12.3, 4.2), uc_pos['UC06'], ew, 'right')
    draw_assoc_line(ax, (12.3, 3.9), uc_pos['UC07'], ew, 'right')
    draw_assoc_line(ax, (12.3, 3.6), uc_pos['UC08'], ew, 'right')
    draw_assoc_line(ax, (12.3, 3.3), uc_pos['UC09'], ew, 'right')
    draw_assoc_line(ax, (12.3, 3.0), uc_pos['UC10'], ew, 'right')

    # Internal relationships
    draw_relation(ax, (uc_center_x, 11.55), (uc_center_x, 11.25), "«include»")
    draw_relation(ax, (uc_center_x, 10.35), (uc_center_x, 10.05), "«include»")

    save_fig(fig, "uc_overall_diagram.png")


# =============================================================
# 2. UC01: Đọc & Tiền Xử Lý Dữ Liệu Cảm Biến (B&W Layered)
# =============================================================
def make_uc01_bw():
    fig, ax = plt.subplots(figsize=(11.5, 7.5), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # System box
    draw_subsystem_box(ax, 4.8, 0.5, 6.2, 6.5, "Phân Hệ Thu Thập & Xử Lý Cảm Biến")

    ew = 4.6
    eh = 0.85
    p_main = draw_ellipse(ax, 7.9, 5.5, ew, eh, "UC01: Đọc & Tiền Xử Lý Dữ Liệu")
    p_sub1 = draw_ellipse(ax, 7.9, 4.0, ew, eh, "Lọc Trung Vị 3 Mẫu (Median Filter)")
    p_sub2 = draw_ellipse(ax, 7.9, 2.6, ew, eh, "Quy Đổi Mực Nước (50cm-5cm -> %)")
    p_sub3 = draw_ellipse(ax, 7.9, 1.2, ew, eh, "Phân Tầng Cấp Mưa (ADC & DO)")

    # Left Actors showing physical interaction chain
    # 1. Environmental stimulus actor
    draw_stick_figure(ax, 1.1, 5.5, "Môi Trường Vật Lý\n(Mặt nước & Mưa)", "«environment»", scale=0.9)

    # 2. Sensor hardware actor
    draw_stick_figure(ax, 3.3, 5.5, "Cảm Biến Ngoại Vi\n(HC-SR04 & FC-37)", "«peripheral»", scale=0.9)

    # Arrow 1: Environment -> Sensor (Physical stimulus)
    ax.annotate("", xy=(2.5, 5.5), xytext=(1.7, 5.5),
                arrowprops=dict(arrowstyle="->", lw=1.3, color="#000000"), zorder=5)
    ax.text(2.1, 5.85, "Tác động\nvật lý", fontsize=7.5, style='italic', ha='center', color='#000000')

    # Arrow 2: Sensor -> UC01 (Electrical signals)
    ax.annotate("", xy=(5.6, 5.5), xytext=(4.1, 5.5),
                arrowprops=dict(arrowstyle="->", lw=1.3, color="#000000"), zorder=5)
    ax.text(4.85, 5.85, "Tín hiệu điện:\nXung Echo & ADC", fontsize=7.5, style='italic', ha='center', color='#000000')

    # Includes inside subsystem
    draw_relation(ax, (7.9, 5.05), (7.9, 4.45), "«include»")
    draw_relation(ax, (7.9, 3.55), (7.9, 3.05), "«include»")
    draw_relation(ax, (7.9, 2.15), (7.9, 1.65), "«include»")

    # Detailed notes at bottom left
    ax.text(2.2, 2.2, "Chuỗi tương tác vật lý:", fontsize=8.5, fontweight='bold', ha='center', color='#000000')
    ax.text(2.2, 1.7, "1. Mặt nước hồ thu dập dềnh\n   phản xạ sóng siêu âm 40kHz.", fontsize=7.5, ha='center', color='#333333')
    ax.text(2.2, 1.1, "2. Hạt mưa rơi làm giảm điện trở\n   mặt tiếp xúc bản cực đồng.", fontsize=7.5, ha='center', color='#333333')
    ax.text(2.2, 0.6, "3. Cảm biến chuyển thành xung\n   và điện áp gửi về ESP32.", fontsize=7.5, ha='center', color='#333333')

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
# 4. UC03: Tự Động Điều Khiển Máy Bơm (B&W Layered)
# =============================================================
def make_uc03_bw():
    fig, ax = plt.subplots(figsize=(11.5, 6), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.5, 0.5, 5.0, 5.0, "Phân Hệ Điều Khiển Máy Bơm")

    ew = 4.2
    eh = 0.8
    p_main = draw_ellipse(ax, 5.0, 4.1, ew, eh, "UC03: Tự Động Điều Khiển Bơm")
    p_on   = draw_ellipse(ax, 5.0, 2.7, ew, eh, "Kích Relay Active LOW (Bật Bơm)")
    p_off  = draw_ellipse(ax, 5.0, 1.3, ew, eh, "Ngắt Bằng High-Z INPUT (Triệt Rò)")

    draw_stick_figure(ax, 1.1, 4.1, "Máy Trạng Thái\nFSM Controller", "«internal»")
    
    # Right side: Actuator -> Physical Impact
    draw_stick_figure(ax, 8.4, 4.1, "Module Relay 5V\n& Máy Bơm Mini", "«actuator»")
    draw_stick_figure(ax, 10.5, 4.1, "Khối Nước Hồ Thu\nCần Tiêu Thoát", "«environment»")

    draw_assoc_line(ax, (1.7, 4.1), p_main, ew, 'left')
    draw_assoc_line(ax, (7.8, 4.1), p_main, ew, 'right')

    # Arrow: Relay/Pump -> Water
    ax.annotate("", xy=(10.0, 4.1), xytext=(9.1, 4.1),
                arrowprops=dict(arrowstyle="->", lw=1.3, color="#000000"), zorder=5)
    ax.text(9.55, 4.45, "Hút xả\nnước lũ", fontsize=7.5, style='italic', ha='center', color='#000000')

    draw_relation(ax, (5.0, 3.7), (5.0, 3.1), "«include»")
    draw_relation(ax, (5.0, 2.3), (5.0, 1.7), "«include»")

    save_fig(fig, "uc03_pump_control.png")


# =============================================================
# 5. UC04: Tự Động Điều Khiển Van Thoát Lũ (B&W Layered)
# =============================================================
def make_uc04_bw():
    fig, ax = plt.subplots(figsize=(11.5, 6), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.5, 0.5, 5.0, 5.0, "Phân Hệ Điều Khiển Van Thoát Lũ")

    ew = 4.2
    eh = 0.8
    p_main = draw_ellipse(ax, 5.0, 4.1, ew, eh, "UC04: Tự Động Điều Khiển Van")
    p_mid  = draw_ellipse(ax, 5.0, 2.7, ew, eh, "Mở Xả 50% Góc 90° (Mức DANGER)")
    p_full = draw_ellipse(ax, 5.0, 1.3, ew, eh, "Mở Xả 100% Góc 180° (CRITICAL)")

    draw_stick_figure(ax, 1.1, 4.1, "Máy Trạng Thái\nFSM Controller", "«internal»")
    draw_stick_figure(ax, 8.4, 4.1, "Động Cơ Servo\nSG90 (GPIO 27)", "«actuator»")
    draw_stick_figure(ax, 10.5, 4.1, "Cửa Cống Xả Lũ\n& Dòng Nước", "«environment»")

    draw_assoc_line(ax, (1.7, 4.1), p_main, ew, 'left')
    draw_assoc_line(ax, (7.8, 4.1), p_main, ew, 'right')

    ax.annotate("", xy=(10.0, 4.1), xytext=(9.1, 4.1),
                arrowprops=dict(arrowstyle="->", lw=1.3, color="#000000"), zorder=5)
    ax.text(9.55, 4.45, "Kéo mở\ncửa van cống", fontsize=7.5, style='italic', ha='center', color='#000000')

    draw_relation(ax, (5.0, 3.7), (5.0, 3.1), "«include»")
    draw_relation(ax, (5.0, 2.3), (5.0, 1.7), "«include»")

    save_fig(fig, "uc04_valve_control.png")


# =============================================================
# 6. UC05: Cảnh Báo LED & Còi Buzzer (B&W Layered)
# =============================================================
def make_uc05_bw():
    fig, ax = plt.subplots(figsize=(11.5, 6), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.5, 0.5, 5.0, 5.0, "Phân Hệ Báo Động Tại Chỗ")

    ew = 4.2
    eh = 0.8
    p_main = draw_ellipse(ax, 5.0, 4.1, ew, eh, "UC05: Báo Động Tại Chỗ (LED & Còi)")
    p_led  = draw_ellipse(ax, 5.0, 2.7, ew, eh, "Chỉ Thị LED Đa Màu (Xanh/Vàng/Đỏ)")
    p_buz  = draw_ellipse(ax, 5.0, 1.3, ew, eh, "Phát Còi Non-blocking (millis)")

    draw_stick_figure(ax, 1.1, 4.1, "Máy Trạng Thái\nFSM Controller", "«internal»")
    draw_stick_figure(ax, 8.4, 4.1, "Cụm 3 LED & Còi\nBuzzer 5V", "«signaling»")
    draw_stick_figure(ax, 10.5, 4.1, "Người Dân &\nKỹ Thuật Viên", "«human»")

    draw_assoc_line(ax, (1.7, 4.1), p_main, ew, 'left')
    draw_assoc_line(ax, (7.8, 4.1), p_main, ew, 'right')

    ax.annotate("", xy=(10.0, 4.1), xytext=(9.1, 4.1),
                arrowprops=dict(arrowstyle="->", lw=1.3, color="#000000"), zorder=5)
    ax.text(9.55, 4.45, "Âm thanh hú\n& ánh sáng", fontsize=7.5, style='italic', ha='center', color='#000000')

    draw_relation(ax, (5.0, 3.7), (5.0, 3.1), "«include»")
    draw_relation(ax, (5.0, 2.3), (5.0, 1.7), "«include»")

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
    print("Generating pure black & white UML Use Case diagrams with explicit physical interaction chains...")
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
    print("All 11 layered black & white diagrams generated successfully!")
