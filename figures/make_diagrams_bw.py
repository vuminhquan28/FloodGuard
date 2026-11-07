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
    print(f"Generated Strict UML B&W (No Overlap): {filename}")

def draw_human_actor(ax, x, y, label, sublabel="«human actor»", scale=1.0):
    """Draws a standard UML human actor stick figure"""
    r = 0.22 * scale
    head = plt.Circle((x, y + 0.38 * scale), r, facecolor='#ffffff', edgecolor='#000000', lw=1.3, zorder=6)
    ax.add_patch(head)
    # Body
    ax.plot([x, x], [y + 0.16 * scale, y - 0.32 * scale], color='#000000', lw=1.4, zorder=6)
    # Arms
    ax.plot([x - 0.28 * scale, x + 0.28 * scale], [y - 0.02 * scale, y - 0.02 * scale], color='#000000', lw=1.4, zorder=6)
    # Legs
    ax.plot([x, x - 0.24 * scale], [y - 0.32 * scale, y - 0.7 * scale], color='#000000', lw=1.4, zorder=6)
    ax.plot([x, x + 0.24 * scale], [y - 0.32 * scale, y - 0.7 * scale], color='#000000', lw=1.4, zorder=6)
    # Label
    ax.text(x, y - 0.85 * scale, label, fontsize=8.5, fontweight='bold', ha='center', va='top', color='#000000')
    if sublabel:
        ax.text(x, y - 1.25 * scale, sublabel, fontsize=7.5, style='italic', ha='center', va='top', color='#333333')
    return (x, y - 0.02 * scale)

def draw_device_actor(ax, x, y, label, sublabel="«device»", w=2.4, h=1.05):
    """Draws a standard UML device actor box"""
    rect = patches.Rectangle((x - w/2, y - h/2), w, h, linewidth=1.3, edgecolor='#000000', facecolor='#ffffff', zorder=6)
    ax.add_patch(rect)
    ax.text(x, y + 0.22, sublabel, fontsize=7.5, style='italic', ha='center', va='center', color='#000000', zorder=7)
    ax.text(x, y - 0.15, label, fontsize=8.2, fontweight='bold', ha='center', va='center', color='#000000', zorder=7)
    return (x, y)

def draw_timer_actor(ax, x, y, label="Bộ Định Thời Timer", sublabel="«internal timer»", w=2.4, h=1.05):
    """Draws an internal timer / clock actor"""
    rect = patches.Rectangle((x - w/2, y - h/2), w, h, linewidth=1.3, edgecolor='#000000', facecolor='#ffffff', zorder=6)
    ax.add_patch(rect)
    ax.text(x, y + 0.22, sublabel, fontsize=7.5, style='italic', ha='center', va='center', color='#000000', zorder=7)
    ax.text(x, y - 0.15, label, fontsize=8.2, fontweight='bold', ha='center', va='center', color='#000000', zorder=7)
    return (x, y)

def draw_subsystem_box(ax, x, y, w, h, title):
    rect = patches.Rectangle((x, y), w, h, linewidth=1.5, edgecolor='#000000', facecolor='#ffffff', zorder=1)
    ax.add_patch(rect)
    ax.text(x + 0.25, y + h - 0.35, "«subsystem»", fontsize=8.5, style='italic', color='#000000')
    ax.text(x + 0.25, y + h - 0.72, title, fontsize=10.0, fontweight='bold', color='#000000')

def draw_ellipse(ax, x, y, w, h, text):
    ellipse = patches.Ellipse((x, y), w, h, facecolor='#ffffff', edgecolor='#000000', lw=1.3, zorder=3)
    ax.add_patch(ellipse)
    ax.text(x, y, text, fontsize=8.2, fontweight='bold', ha='center', va='center', color='#000000', zorder=4)
    return (x, y)

def draw_assoc_line(ax, pt_from, pt_to, ew=0, side='left'):
    """Draws a solid association line between an actor and a use case ellipse border"""
    fx, fy = pt_from
    tx, ty = pt_to
    if ew > 0:
        if side == 'left':
            tx_target = tx - (ew / 2)
        else:
            tx_target = tx + (ew / 2)
    else:
        tx_target = tx
    ax.plot([fx, tx_target], [fy, ty], color='#000000', lw=1.1, zorder=2)

def draw_include(ax, pt_from, pt_to, label="«include»"):
    """
    Draws a clean dashed arrow from Parent UC to Child UC.
    Label is enclosed in an opaque white pill to prevent any overlap.
    """
    ax.annotate("", xy=pt_to, xytext=pt_from,
                arrowprops=dict(arrowstyle="->", lw=1.2, linestyle="--", color="#000000"), zorder=4)
    mid_x = (pt_from[0] + pt_to[0]) / 2
    mid_y = (pt_from[1] + pt_to[1]) / 2
    ax.text(mid_x, mid_y, label, fontsize=7.5, style='italic', color='#000000', 
            ha='center', va='center', zorder=6,
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#ffffff', edgecolor='#000000', lw=0.6))

def draw_extend(ax, pt_from, pt_to, label="«extend»"):
    """
    Draws a clean dashed arrow from Extension UC back to Base UC.
    Label is enclosed in an opaque white pill to prevent any overlap.
    """
    ax.annotate("", xy=pt_to, xytext=pt_from,
                arrowprops=dict(arrowstyle="->", lw=1.2, linestyle="--", color="#000000"), zorder=4)
    mid_x = (pt_from[0] + pt_to[0]) / 2
    mid_y = (pt_from[1] + pt_to[1]) / 2
    ax.text(mid_x, mid_y, label, fontsize=7.2, style='italic', color='#000000', 
            ha='center', va='center', zorder=6,
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#ffffff', edgecolor='#000000', lw=0.6))


# =============================================================
# 1. OVERALL SYSTEM USE CASE DIAGRAM (Strict UML 2.5)
# Zero overlap, cleanly separated primary actors (left) and secondary actors (right)
# =============================================================
def make_overall_uml_bw():
    fig, ax = plt.subplots(figsize=(16.5, 14.8), dpi=300)
    ax.set_xlim(0, 16.5)
    ax.set_ylim(0, 14.8)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    sys_x = 3.6
    sys_y = 0.5
    sys_w = 9.0
    sys_h = 13.8
    draw_subsystem_box(ax, sys_x, sys_y, sys_w, sys_h, 
                       "Hệ Thống Trạm FloodGuard (ESP32 Firmware)")

    uc_center_x = 8.1
    uc_list = [
        ("UC01: Đọc & Tiền Xử Lý Dữ Liệu Cảm Biến", 12.2),
        ("UC02: Tự Động Đánh Giá FSM & Dải Trễ", 11.0),
        ("UC03: Tự Động Điều Khiển Máy Bơm", 9.8),
        ("UC04: Tự Động Điều Khiển Van Thoát Lũ", 8.6),
        ("UC05: Phát Cảnh Báo LED & Còi Tại Chỗ", 7.4),
        ("UC06: Tự Động Chuyển An Toàn (Failsafe)", 6.2),
        ("UC07: Truyền Nhận Dữ Liệu Web API", 5.0),
        ("UC08: Giám Sát Trạng Thái Trạm Qua Web", 3.8),
        ("UC09: Chuyển Đổi Chế Độ (AUTO / MANUAL)", 2.6),
        ("UC10: Can Thiệp Cưỡng Chế Thiết Bị Từ Web", 1.4)
    ]

    uc_pos = {}
    ew = 6.2
    eh = 0.85
    for name, cy in uc_list:
        pt = draw_ellipse(ax, uc_center_x, cy, ew, eh, name)
        uc_pos[name[:4]] = pt

    # PRIMARY ACTORS (LEFT)
    # 1. Internal Timer
    draw_timer_actor(ax, 1.4, 11.4, "Bộ Định Thời\nTimer / Watchdog", "«internal timer»", w=2.4, h=1.1)
    draw_assoc_line(ax, (2.6, 11.9), uc_pos['UC01'], ew, 'left')
    draw_assoc_line(ax, (2.6, 11.4), uc_pos['UC02'], ew, 'left')
    draw_assoc_line(ax, (2.6, 10.9), uc_pos['UC06'], ew, 'left')

    # 2. Human Operator
    draw_human_actor(ax, 1.4, 3.8, "Người Vận Hành", "«human actor»", scale=0.95)
    draw_assoc_line(ax, (2.3, 4.4), uc_pos['UC07'], ew, 'left')
    draw_assoc_line(ax, (2.3, 3.8), uc_pos['UC08'], ew, 'left')
    draw_assoc_line(ax, (2.3, 3.2), uc_pos['UC09'], ew, 'left')
    draw_assoc_line(ax, (2.3, 2.6), uc_pos['UC10'], ew, 'left')

    # SECONDARY ACTORS (RIGHT)
    # 3. Sensors
    draw_device_actor(ax, 15.0, 12.2, "Cảm Biến Siêu Âm\n& Cảm Biến Mưa", "«device»", w=2.5, h=1.1)
    draw_assoc_line(ax, (13.75, 12.2), uc_pos['UC01'], ew, 'right')

    # 4. Pump & Relay
    draw_device_actor(ax, 15.0, 9.8, "Module Relay 5V\n& Máy Bơm Mini", "«device»", w=2.5, h=1.1)
    draw_assoc_line(ax, (13.75, 9.8), uc_pos['UC03'], ew, 'right')

    # 5. Servo Gate
    draw_device_actor(ax, 15.0, 8.6, "Động Cơ Servo\nSG90 (Cửa Van)", "«device»", w=2.5, h=1.1)
    draw_assoc_line(ax, (13.75, 8.6), uc_pos['UC04'], ew, 'right')

    # 6. Signaling LEDs & Buzzer
    draw_device_actor(ax, 15.0, 7.4, "Cụm 3 Đèn LED\n& Còi Buzzer 5V", "«device»", w=2.5, h=1.1)
    draw_assoc_line(ax, (13.75, 7.4), uc_pos['UC05'], ew, 'right')

    # 7. Local Residents
    draw_human_actor(ax, 15.0, 5.0, "Người Dân\nQuanh Trạm", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (14.1, 5.4), uc_pos['UC05'], ew, 'right')

    # 8. Override Actuators target for UC10
    draw_device_actor(ax, 15.0, 1.4, "Thiết Bị Bơm\n& Van Cưỡng Chế", "«device»", w=2.5, h=1.1)
    draw_assoc_line(ax, (13.75, 1.4), uc_pos['UC10'], ew, 'right')

    save_fig(fig, "uc_overall_diagram.png")


# =============================================================
# 2. UC01: Đọc & Tiền Xử Lý Dữ Liệu Cảm Biến (Fan-out Layout)
# =============================================================
def make_uc01_bw():
    fig, ax = plt.subplots(figsize=(15.2, 7.5), dpi=300)
    ax.set_xlim(0, 15.2)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 9.6, 6.5, 
                       "Phân Hệ Đo Đạc Cảm Biến (ESP32 Firmware)")

    # Base UC centered on left
    p_main = draw_ellipse(ax, 4.8, 3.6, 3.6, 1.05, "UC01: Đọc & Tiền Xử Lý\nDữ Liệu Cảm Biến")
    
    # 3 Included Children vertically distributed on the right
    p_sub1 = draw_ellipse(ax, 10.0, 5.5, 4.4, 0.9, "Đo Khoảng Cách Siêu Âm\n(HC-SR04 Trigger / Echo)")
    p_sub2 = draw_ellipse(ax, 10.0, 3.6, 4.4, 0.9, "Lọc Trung Vị 3 Mẫu &\nQuy Đổi % Mực Nước")
    p_sub3 = draw_ellipse(ax, 10.0, 1.7, 4.4, 0.9, "Đọc Cảm Biến Mưa &\nPhân Cấp Tương Tự ADC/DO")

    # Left Actors
    draw_timer_actor(ax, 1.3, 4.8, "Bộ Định Thời\nTimer 100ms", "«internal timer»", w=2.3, h=1.1)
    draw_assoc_line(ax, (2.45, 4.8), (p_main[0] - 1.8, 4.0))

    draw_device_actor(ax, 1.3, 2.4, "Cảm Biến HC-SR04\n& Cảm Biến Mưa", "«device»", w=2.3, h=1.1)
    draw_assoc_line(ax, (2.45, 2.4), (p_main[0] - 1.8, 3.2))

    # Fanning included arrows from right edge of p_main
    draw_include(ax, (p_main[0] + 1.8, 4.1), (p_sub1[0] - 2.2, 5.5), "«include»")
    draw_include(ax, (p_main[0] + 1.8, 3.6), (p_sub2[0] - 2.2, 3.6), "«include»")
    draw_include(ax, (p_main[0] + 1.8, 3.1), (p_sub3[0] - 2.2, 1.7), "«include»")

    save_fig(fig, "uc01_sensor_processing.png")


# =============================================================
# 3. UC02: Đánh Giá FSM & Xử Lý Dải Trễ (Fan-out Layout)
# =============================================================
def make_uc02_bw():
    fig, ax = plt.subplots(figsize=(15.2, 7.5), dpi=300)
    ax.set_xlim(0, 15.2)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 9.6, 6.5, 
                       "Phân Hệ Logic FSM & Dải Trễ (ESP32 Firmware)")

    # Base UC on left
    p_main = draw_ellipse(ax, 4.8, 3.6, 3.6, 1.05, "UC02: Tự Động Đánh Giá\nFSM & Dải Trễ")
    
    # 2 Included Children fanning out on the right
    p_sub1 = draw_ellipse(ax, 10.0, 5.0, 4.4, 0.95, "Đánh Giá 4 Cấp Độ Cảnh Báo\n(NORMAL - CRITICAL)")
    p_sub2 = draw_ellipse(ax, 10.0, 2.2, 4.4, 0.95, "Áp Dụng Dải Trễ Hysteresis\nChống Rung Giật (Chattering)")

    draw_timer_actor(ax, 1.3, 3.6, "Bộ Định Thời\nChu Kỳ FSM", "«internal timer»", w=2.3, h=1.1)
    draw_assoc_line(ax, (2.45, 3.6), (p_main[0] - 1.8, 3.6))

    # Fanning arrows
    draw_include(ax, (p_main[0] + 1.8, 4.1), (p_sub1[0] - 2.2, 5.0), "«include»")
    draw_include(ax, (p_main[0] + 1.8, 3.1), (p_sub2[0] - 2.2, 2.2), "«include»")

    save_fig(fig, "uc02_fsm_hysteresis.png")


# =============================================================
# 4. UC03: Tự Động Điều Khiển Máy Bơm (Fan-out Layout)
# =============================================================
def make_uc03_bw():
    fig, ax = plt.subplots(figsize=(15.5, 7.5), dpi=300)
    ax.set_xlim(0, 15.5)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 9.4, 6.5, 
                       "Phân Hệ Điều Khiển Bơm (ESP32 Firmware)")

    p_main = draw_ellipse(ax, 4.7, 3.6, 3.4, 1.05, "UC03: Tự Động Điều Khiển\nMáy Bơm Thoát Nước")
    
    p_on  = draw_ellipse(ax, 9.7, 5.0, 4.0, 0.95, "Kích Relay Active LOW\n(Bật Bơm Thoát Nước)")
    p_off = draw_ellipse(ax, 9.7, 2.2, 4.0, 0.95, "Thả Nổi High-Z INPUT\n(Ngắt Bơm An Toàn)")

    draw_timer_actor(ax, 1.3, 3.6, "Trình Điều Phối\nFSM ESP32", "«internal timer»", w=2.3, h=1.1)
    draw_assoc_line(ax, (2.45, 3.6), (p_main[0] - 1.7, 3.6))

    draw_device_actor(ax, 13.8, 3.6, "Module Relay 5V\n& Máy Bơm Mini", "«device»", w=2.5, h=1.1)
    draw_assoc_line(ax, (p_on[0] + 2.0, 5.0), (12.55, 3.9))
    draw_assoc_line(ax, (p_off[0] + 2.0, 2.2), (12.55, 3.3))

    draw_include(ax, (p_main[0] + 1.7, 4.1), (p_on[0] - 2.0, 5.0), "«include»")
    draw_include(ax, (p_main[0] + 1.7, 3.1), (p_off[0] - 2.0, 2.2), "«include»")

    save_fig(fig, "uc03_pump_control.png")


# =============================================================
# 5. UC04: Tự Động Điều Khiển Van Thoát Lũ (Fan-out Layout)
# =============================================================
def make_uc04_bw():
    fig, ax = plt.subplots(figsize=(15.5, 7.5), dpi=300)
    ax.set_xlim(0, 15.5)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 9.4, 6.5, 
                       "Phân Hệ Điều Khiển Van Lũ (ESP32 Firmware)")

    p_main = draw_ellipse(ax, 4.7, 3.6, 3.4, 1.05, "UC04: Tự Động Điều Khiển\nVan Thoát Lũ")
    
    p_mid  = draw_ellipse(ax, 9.7, 5.0, 4.0, 0.95, "Xuất PWM Mở Van 50%\n(Góc 90° Mức DANGER)")
    p_full = draw_ellipse(ax, 9.7, 2.2, 4.0, 0.95, "Xuất PWM Mở Van 100%\n(Góc 180° CRITICAL)")

    draw_timer_actor(ax, 1.3, 3.6, "Trình Điều Phối\nFSM ESP32", "«internal timer»", w=2.3, h=1.1)
    draw_assoc_line(ax, (2.45, 3.6), (p_main[0] - 1.7, 3.6))

    draw_device_actor(ax, 13.8, 3.6, "Động Cơ Servo\nSG90 (GPIO 27)", "«device»", w=2.5, h=1.1)
    draw_assoc_line(ax, (p_mid[0] + 2.0, 5.0), (12.55, 3.9))
    draw_assoc_line(ax, (p_full[0] + 2.0, 2.2), (12.55, 3.3))

    draw_include(ax, (p_main[0] + 1.7, 4.1), (p_mid[0] - 2.0, 5.0), "«include»")
    draw_include(ax, (p_main[0] + 1.7, 3.1), (p_full[0] - 2.0, 2.2), "«include»")

    save_fig(fig, "uc04_valve_control.png")


# =============================================================
# 6. UC05: Cảnh Báo LED & Còi Buzzer (Fan-out Layout)
# =============================================================
def make_uc05_bw():
    fig, ax = plt.subplots(figsize=(15.5, 7.5), dpi=300)
    ax.set_xlim(0, 15.5)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 9.4, 6.5, 
                       "Phân Hệ Cảnh Báo Tại Chỗ (ESP32 Firmware)")

    p_main = draw_ellipse(ax, 4.7, 3.6, 3.4, 1.05, "UC05: Phát Cảnh Báo\nLED & Còi Tại Chỗ")
    
    p_led = draw_ellipse(ax, 9.7, 5.0, 4.0, 0.95, "Chỉ Thị LED Trực Quan\n(Xanh / Vàng / Đỏ)")
    p_buz = draw_ellipse(ax, 9.7, 2.2, 4.0, 0.95, "Kích Âm Còi Báo Động\nNon-blocking (millis)")

    draw_timer_actor(ax, 1.3, 3.6, "Trình Điều Phối\nFSM ESP32", "«internal timer»", w=2.3, h=1.1)
    draw_assoc_line(ax, (2.45, 3.6), (p_main[0] - 1.7, 3.6))

    draw_device_actor(ax, 13.8, 5.0, "Cụm 3 Đèn LED\n& Còi Buzzer 5V", "«device»", w=2.5, h=1.1)
    draw_assoc_line(ax, (p_led[0] + 2.0, 5.0), (12.55, 5.0))

    draw_human_actor(ax, 13.8, 2.2, "Người Dân\nQuanh Trạm", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (p_buz[0] + 2.0, 2.2), (12.8, 2.2))

    draw_include(ax, (p_main[0] + 1.7, 4.1), (p_led[0] - 2.0, 5.0), "«include»")
    draw_include(ax, (p_main[0] + 1.7, 3.1), (p_buz[0] - 2.0, 2.2), "«include»")

    save_fig(fig, "uc05_signaling_buzzer_led.png")


# =============================================================
# 7. UC06: Failsafe to AUTO (Fan-out Layout)
# =============================================================
def make_uc06_bw():
    fig, ax = plt.subplots(figsize=(15.5, 7.5), dpi=300)
    ax.set_xlim(0, 15.5)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 9.4, 6.5, 
                       "Phân Hệ Tự Trị Failsafe (ESP32 Firmware)")

    p_main = draw_ellipse(ax, 4.7, 3.6, 3.4, 1.05, "UC06: Tự Động Chuyển\nAn Toàn Về AUTO")
    
    p_chk = draw_ellipse(ax, 9.7, 5.0, 4.0, 0.95, "Kiểm Tra Timeout\nKết Nối Wi-Fi / Web")
    p_fsm = draw_ellipse(ax, 9.7, 2.2, 4.0, 0.95, "Cưỡng Chế Đảo Cờ\nisAutoMode = true")

    draw_timer_actor(ax, 1.3, 3.6, "Bộ Giám Sát\nWatchdog / Timeout", "«internal timer»", w=2.4, h=1.1)
    draw_assoc_line(ax, (2.5, 3.6), (p_main[0] - 1.7, 3.6))

    draw_human_actor(ax, 13.8, 3.6, "Người Vận Hành\n(Mất Kết Nối)", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (p_chk[0] + 2.0, 5.0), (12.9, 4.0))
    draw_assoc_line(ax, (p_fsm[0] + 2.0, 2.2), (12.9, 3.2))

    draw_include(ax, (p_main[0] + 1.7, 4.1), (p_chk[0] - 2.0, 5.0), "«include»")
    draw_include(ax, (p_main[0] + 1.7, 3.1), (p_fsm[0] - 2.0, 2.2), "«include»")

    save_fig(fig, "uc06_network_failsafe.png")


# =============================================================
# 8. UC07: Truyền Nhận Telemetry & API (Fan-out Layout)
# =============================================================
def make_uc07_bw():
    fig, ax = plt.subplots(figsize=(15.5, 7.5), dpi=300)
    ax.set_xlim(0, 15.5)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 9.4, 6.5, 
                       "Phân Hệ Web Server & REST API (ESP32)")

    p_main = draw_ellipse(ax, 4.7, 3.6, 3.4, 1.05, "UC07: Truyền Nhận\nDữ Liệu Web API")
    
    p_stat = draw_ellipse(ax, 9.7, 5.0, 4.0, 0.95, "Đóng Gói Dữ Liệu JSON\n(GET /api/status)")
    p_cmd  = draw_ellipse(ax, 9.7, 2.2, 4.0, 0.95, "Tiếp Nhận Gói Lệnh\n(GET /api/control)")

    draw_human_actor(ax, 1.3, 3.6, "Người Vận Hành", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (2.2, 3.6), (p_main[0] - 1.7, 3.6))

    draw_device_actor(ax, 13.8, 3.6, "ESP32 Web Server\n(Port 80 HTTP)", "«server»", w=2.4, h=1.1)
    draw_assoc_line(ax, (p_stat[0] + 2.0, 5.0), (12.6, 3.9))
    draw_assoc_line(ax, (p_cmd[0] + 2.0, 2.2), (12.6, 3.3))

    draw_include(ax, (p_main[0] + 1.7, 4.1), (p_stat[0] - 2.0, 5.0), "«include»")
    draw_include(ax, (p_main[0] + 1.7, 3.1), (p_cmd[0] - 2.0, 2.2), "«include»")

    save_fig(fig, "uc07_telemetry_api.png")


# =============================================================
# 9. UC08: Giám Sát Web Dashboard (Fan-out Layout)
# =============================================================
def make_uc08_bw():
    fig, ax = plt.subplots(figsize=(15.2, 7.5), dpi=300)
    ax.set_xlim(0, 15.2)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 9.6, 6.5, 
                       "Phân Hệ Web Dashboard (ESP32 Web App)")

    p_main = draw_ellipse(ax, 4.8, 3.6, 3.6, 1.05, "UC08: Giám Sát Trạng Thái\nTrạm Qua Web Dashboard")
    
    p_bar = draw_ellipse(ax, 10.0, 5.0, 4.4, 0.95, "Hiển Thị Đồng Hồ Mực Nước\n(% và Khoảng Cách cm)")
    p_dev = draw_ellipse(ax, 10.0, 2.2, 4.4, 0.95, "Cập Nhật Trạng Thái Thiết Bị\n(Bơm, Van, LED, Còi)")

    draw_human_actor(ax, 1.3, 3.6, "Người Vận Hành", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (2.2, 3.6), (p_main[0] - 1.8, 3.6))

    draw_include(ax, (p_main[0] + 1.8, 4.1), (p_bar[0] - 2.2, 5.0), "«include»")
    draw_include(ax, (p_main[0] + 1.8, 3.1), (p_dev[0] - 2.2, 2.2), "«include»")

    save_fig(fig, "uc08_web_dashboard.png")


# =============================================================
# 10. UC09: Chuyển Đổi AUTO/MANUAL (Strict UML «extend» Fork Layout)
# Base UC on Top Center, 2 Extensions on Bottom fanning inward and UPWARD to Base UC.
# =============================================================
def make_uc09_bw():
    fig, ax = plt.subplots(figsize=(15.2, 7.8), dpi=300)
    ax.set_xlim(0, 15.2)
    ax.set_ylim(0, 7.8)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 11.6, 6.8, 
                       "Phân Hệ Quản Lý Chế Độ (ESP32 Firmware)")

    # Base Use Case on Top Center
    p_main = draw_ellipse(ax, 8.6, 5.6, 4.8, 1.05, "UC09: Chuyển Đổi Chế Độ Vận Hành")
    
    # 2 Extension Use Cases spread horizontally below
    p_auto = draw_ellipse(ax, 5.8, 2.2, 4.2, 0.95, "Khóa Phím Web, Giao Quyền\nTự Động Cho FSM")
    p_manu = draw_ellipse(ax, 11.4, 2.2, 4.2, 0.95, "Mở Khóa Nút Bấm, Cho Phép\nCan Thiệp Thủ Công")

    draw_human_actor(ax, 1.3, 5.6, "Người Vận Hành", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (2.2, 5.6), (p_main[0] - 2.4, 5.6))

    # Converging extend arrows from children UPWARD to Base UC
    draw_extend(ax, (p_auto[0] + 0.8, 2.7), (p_main[0] - 1.0, 5.1), "«extend»\n[chọn AUTO]")
    draw_extend(ax, (p_manu[0] - 0.8, 2.7), (p_main[0] + 1.0, 5.1), "«extend»\n[chọn MANUAL]")

    save_fig(fig, "uc09_mode_switch.png")


# =============================================================
# 11. UC10: Can Thiệp Cưỡng Chế Thiết Bị (Strict UML «extend» Layout)
# Base UC on Top Center, 2 Extensions below fanning inward and UPWARD to Base UC.
# Pump Module placed on Left, Servo Motor on Right -> ZERO line crossing!
# =============================================================
def make_uc10_bw():
    fig, ax = plt.subplots(figsize=(15.8, 7.8), dpi=300)
    ax.set_xlim(0, 15.8)
    ax.set_ylim(0, 7.8)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 9.8, 6.8, 
                       "Phân Hệ Can Thiệp Cưỡng Chế (ESP32 Firmware)")

    # Base Use Case on Top Center
    p_main = draw_ellipse(ax, 7.7, 5.6, 4.8, 1.05, "UC10: Can Thiệp Cưỡng Chế Thiết Bị Từ Web")
    
    # 2 Extension Use Cases spread horizontally below
    p_pump = draw_ellipse(ax, 5.4, 2.2, 3.8, 0.95, "Bật / Tắt Cưỡng Chế\nMáy Bơm Thoát Nước")
    p_gate = draw_ellipse(ax, 10.0, 2.2, 3.8, 0.95, "Điều Khiển Cưỡng Chế\nGóc Van (0° / 90° / 180°)")

    # Human operator at top left
    draw_human_actor(ax, 1.3, 5.6, "Người Vận Hành", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (2.2, 5.6), (p_main[0] - 2.4, 5.6))

    # Converging extend arrows from children UPWARD to Base UC
    draw_extend(ax, (p_pump[0] + 0.6, 2.7), (p_main[0] - 0.9, 5.1), "«extend»\n[lệnh Bơm]")
    draw_extend(ax, (p_gate[0] - 0.6, 2.7), (p_main[0] + 0.9, 5.1), "«extend»\n[lệnh Van]")

    # Connected actuator devices:
    # Pump Relay device on LEFT -> straight to p_pump (no crossing!)
    draw_device_actor(ax, 1.3, 2.2, "Module Relay 5V\n& Máy Bơm Mini", "«device»", w=2.4, h=1.05)
    draw_assoc_line(ax, (2.5, 2.2), (p_pump[0] - 1.9, 2.2))

    # Servo Motor device on RIGHT -> straight to p_gate (no crossing!)
    draw_device_actor(ax, 14.2, 2.2, "Động Cơ Servo\nSG90 (Van Lũ)", "«device»", w=2.4, h=1.05)
    draw_assoc_line(ax, (p_gate[0] + 1.9, 2.2), (13.0, 2.2))

    save_fig(fig, "uc10_manual_override.png")


if __name__ == "__main__":
    print("Generating pure black & white UML Use Case diagrams with zero overlap...")
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
    print("All 11 clean UML diagrams generated successfully!")
