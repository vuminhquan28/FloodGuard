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
    print(f"Generated Strict UML B&W: {filename}")

def draw_human_actor(ax, x, y, label, sublabel=None, scale=1.0):
    """Draws a standard UML human actor stick figure"""
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
    return (x, y - 0.02 * scale)

def draw_device_actor(ax, x, y, label, sublabel="«device»", w=2.2, h=1.05):
    """Draws a standard UML device actor box"""
    rect = patches.Rectangle((x - w/2, y - h/2), w, h, linewidth=1.3, edgecolor='#000000', facecolor='#ffffff', zorder=5)
    ax.add_patch(rect)
    ax.text(x, y + 0.22, sublabel, fontsize=7.5, style='italic', ha='center', va='center', color='#000000', zorder=6)
    ax.text(x, y - 0.15, label, fontsize=8.5, fontweight='bold', ha='center', va='center', color='#000000', zorder=6)
    return (x, y)

def draw_timer_actor(ax, x, y, label="Bộ Định Thời Timer", sublabel="«internal timer»", w=2.2, h=1.05):
    """Draws an internal timer / clock actor"""
    rect = patches.Rectangle((x - w/2, y - h/2), w, h, linewidth=1.3, edgecolor='#000000', facecolor='#ffffff', zorder=5)
    ax.add_patch(rect)
    ax.text(x, y + 0.22, sublabel, fontsize=7.5, style='italic', ha='center', va='center', color='#000000', zorder=6)
    ax.text(x, y - 0.15, label, fontsize=8.5, fontweight='bold', ha='center', va='center', color='#000000', zorder=6)
    return (x, y)

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

def draw_include(ax, pt_parent, pt_child, label="«include»"):
    """
    Draws a dashed arrow from Parent UC to Child UC.
    In UML, «include» points from base UC to included UC.
    """
    ax.annotate("", xy=pt_child, xytext=pt_parent,
                arrowprops=dict(arrowstyle="->", lw=1.1, linestyle="--", color="#000000"), zorder=3)
    mid_x = (pt_parent[0] + pt_child[0]) / 2 + 0.15
    mid_y = (pt_parent[1] + pt_child[1]) / 2
    ax.text(mid_x, mid_y, label, fontsize=7.5, style='italic', color='#000000', va='center')

def draw_extend(ax, pt_extension, pt_base, label="«extend»"):
    """
    Draws a dashed arrow from Extension UC to Base UC.
    In UML, «extend» points from extending UC back to base UC.
    """
    ax.annotate("", xy=pt_base, xytext=pt_extension,
                arrowprops=dict(arrowstyle="->", lw=1.1, linestyle="--", color="#000000"), zorder=3)
    mid_x = (pt_extension[0] + pt_base[0]) / 2 + 0.15
    mid_y = (pt_extension[1] + pt_base[1]) / 2
    ax.text(mid_x, mid_y, label, fontsize=7.5, style='italic', color='#000000', va='center')


# =============================================================
# 1. OVERALL SYSTEM USE CASE DIAGRAM (Strict UML 2.5)
# Primary Actor (Left): Người Vận Hành & Bộ Định Thời Timer
# Secondary Actors (Right): Cảm Biến, Bơm, Servo, LED/Còi, Người Dân Quanh Trạm
# Independent Use Cases: NO invalid include/dataflow chaining!
# =============================================================
def make_overall_uml_bw():
    fig, ax = plt.subplots(figsize=(16.0, 14.8), dpi=300)
    ax.set_xlim(0, 16.0)
    ax.set_ylim(0, 14.8)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Subsystem box: ESP32 Firmware Controller
    sys_x = 3.6
    sys_y = 0.5
    sys_w = 8.6
    sys_h = 13.8
    draw_subsystem_box(ax, sys_x, sys_y, sys_w, sys_h, 
                       "Hệ Thống Trạm FloodGuard (ESP32 Firmware)")

    uc_center_x = 7.9
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
    ew = 5.8
    eh = 0.85
    for name, cy in uc_list:
        pt = draw_ellipse(ax, uc_center_x, cy, ew, eh, name)
        uc_pos[name[:4]] = pt

    # LEFT SIDE: PRIMARY ACTORS
    # 1. Human Operator
    pt_op = draw_human_actor(ax, 1.4, 3.8, "Người Vận Hành", "«human actor»", scale=0.95)
    # Operator connects to Web-facing use cases
    draw_assoc_line(ax, (2.3, 4.4), uc_pos['UC07'], ew, 'left')
    draw_assoc_line(ax, (2.3, 3.8), uc_pos['UC08'], ew, 'left')
    draw_assoc_line(ax, (2.3, 3.2), uc_pos['UC09'], ew, 'left')
    draw_assoc_line(ax, (2.3, 2.6), uc_pos['UC10'], ew, 'left')

    # 2. Internal Timer / Scheduler
    pt_tm = draw_timer_actor(ax, 1.4, 11.2, "Bộ Định Thời\nTimer / Watchdog", "«internal timer»", w=2.4, h=1.1)
    # Timer activates autonomous monitoring and failsafe
    draw_assoc_line(ax, (2.6, 11.8), uc_pos['UC01'], ew, 'left')
    draw_assoc_line(ax, (2.6, 11.2), uc_pos['UC02'], ew, 'left')
    draw_assoc_line(ax, (2.6, 10.6), uc_pos['UC06'], ew, 'left')

    # RIGHT SIDE: SECONDARY ACTORS («device» & Human Receiver)
    # 3. Input Sensors
    pt_sens = draw_device_actor(ax, 14.5, 12.2, "Cảm Biến Siêu Âm\n& Cảm Biến Mưa", "«device»", w=2.5, h=1.1)
    draw_assoc_line(ax, (13.25, 12.2), uc_pos['UC01'], ew, 'right')

    # 4. Pump & Relay
    pt_pump = draw_device_actor(ax, 14.5, 9.8, "Module Relay 5V\n& Máy Bơm Mini", "«device»", w=2.5, h=1.1)
    draw_assoc_line(ax, (13.25, 9.8), uc_pos['UC03'], ew, 'right')
    draw_assoc_line(ax, (13.25, 9.5), uc_pos['UC10'], ew, 'right')

    # 5. Servo Gate
    pt_servo = draw_device_actor(ax, 14.5, 8.6, "Động Cơ Servo\nSG90 (Cửa Van)", "«device»", w=2.5, h=1.1)
    draw_assoc_line(ax, (13.25, 8.6), uc_pos['UC04'], ew, 'right')
    draw_assoc_line(ax, (13.25, 8.3), uc_pos['UC10'], ew, 'right')

    # 6. Signaling LEDs & Buzzer
    pt_alert = draw_device_actor(ax, 14.5, 6.8, "Cụm 3 Đèn LED\n& Còi Buzzer 5V", "«device»", w=2.5, h=1.1)
    draw_assoc_line(ax, (13.25, 7.1), uc_pos['UC05'], ew, 'right')

    # 7. Local Residents
    pt_res = draw_human_actor(ax, 14.5, 4.4, "Người Dân\nQuanh Trạm", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (13.6, 4.8), uc_pos['UC05'], ew, 'right')

    # NOTE: NO invalid include arrows between UC01 -> UC02 -> UC03!
    save_fig(fig, "uc_overall_diagram.png")


# =============================================================
# 2. UC01: Đọc & Tiền Xử Lý Dữ Liệu Cảm Biến (Proper «include»)
# All 3 included UCs branch directly from UC01 (no chaining)
# =============================================================
def make_uc01_bw():
    fig, ax = plt.subplots(figsize=(12.0, 7.2), dpi=300)
    ax.set_xlim(0, 12.0)
    ax.set_ylim(0, 7.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.9, 0.5, 8.8, 6.2, 
                       "Phân Hệ Đo Đạc Cảm Biến (ESP32 Firmware)")

    ew = 5.2
    eh = 0.82
    p_main = draw_ellipse(ax, 5.8, 5.2, ew, eh, "UC01: Đọc & Tiền Xử Lý Dữ Liệu")
    
    # Children UCs included by UC01
    p_sub1 = draw_ellipse(ax, 9.0, 3.8, 4.4, 0.78, "Đo Khoảng Cách Siêu Âm (HC-SR04)")
    p_sub2 = draw_ellipse(ax, 9.0, 2.4, 4.4, 0.78, "Lọc Trung Vị 3 Mẫu & Tính % Nước")
    p_sub3 = draw_ellipse(ax, 9.0, 1.0, 4.4, 0.78, "Đọc Tín Hiệu Mưa & Phân Cấp ADC/DO")

    # Actors
    pt_tm = draw_timer_actor(ax, 1.4, 5.2, "Bộ Định Thời\nTimer 100ms", "«internal timer»", w=2.4, h=1.1)
    draw_assoc_line(ax, (2.6, 5.2), p_main, ew, 'left')

    pt_dev = draw_device_actor(ax, 1.4, 2.4, "Cảm Biến HC-SR04\n& Cảm Biến Mưa", "«device»", w=2.4, h=1.1)
    draw_assoc_line(ax, (2.6, 2.4), p_main, ew, 'left')

    # Strict UML: All «include» arrows emanate directly from base UC01 to child UCs
    draw_include(ax, (p_main[0] + 1.8, p_main[1] - 0.35), (p_sub1[0] - 2.0, p_sub1[1]))
    draw_include(ax, (p_main[0] + 1.2, p_main[1] - 0.40), (p_sub2[0] - 2.1, p_sub2[1]))
    draw_include(ax, (p_main[0] + 0.6, p_main[1] - 0.42), (p_sub3[0] - 2.2, p_sub3[1]))

    save_fig(fig, "uc01_sensor_processing.png")


# =============================================================
# 3. UC02: Đánh Giá FSM & Xử Lý Dải Trễ (Proper «include»)
# =============================================================
def make_uc02_bw():
    fig, ax = plt.subplots(figsize=(11.5, 6.5), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.9, 0.5, 8.2, 5.5, 
                       "Phân Hệ Logic FSM & Dải Trễ (ESP32 Firmware)")

    ew = 4.8
    eh = 0.82
    p_main = draw_ellipse(ax, 5.6, 4.6, ew, eh, "UC02: Đánh Giá FSM & Dải Trễ")
    
    p_sub1 = draw_ellipse(ax, 8.6, 2.8, 4.6, 0.78, "Đánh Giá 4 Cấp Độ (NORMAL - CRITICAL)")
    p_sub2 = draw_ellipse(ax, 8.6, 1.2, 4.6, 0.78, "Áp Dụng Dải Trễ Hysteresis Chống Rung")

    pt_tm = draw_timer_actor(ax, 1.4, 4.6, "Bộ Định Thời\nChu Kỳ FSM", "«internal timer»", w=2.4, h=1.1)
    draw_assoc_line(ax, (2.6, 4.6), p_main, ew, 'left')

    # All include arrows emanate from parent UC02
    draw_include(ax, (p_main[0] + 1.6, p_main[1] - 0.35), (p_sub1[0] - 2.2, p_sub1[1]))
    draw_include(ax, (p_main[0] + 0.8, p_main[1] - 0.41), (p_sub2[0] - 2.2, p_sub2[1]))

    save_fig(fig, "uc02_fsm_hysteresis.png")


# =============================================================
# 4. UC03: Tự Động Điều Khiển Máy Bơm (Proper «include»)
# =============================================================
def make_uc03_bw():
    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 5.8, 5.2, 
                       "Phân Hệ Điều Khiển Bơm (ESP32 Firmware)")

    ew = 4.6
    eh = 0.82
    p_main = draw_ellipse(ax, 5.6, 4.3, ew, eh, "UC03: Tự Động Điều Khiển Bơm")
    p_on   = draw_ellipse(ax, 5.6, 2.8, 4.8, 0.78, "Kích Relay Active LOW (Bật Bơm Khi Nguy Cấp)")
    p_off  = draw_ellipse(ax, 5.6, 1.3, 4.8, 0.78, "Thả Nổi High-Z INPUT (Ngắt Bơm An Toàn)")

    pt_tm = draw_timer_actor(ax, 1.3, 4.3, "Trình Điều Phối\nFSM ESP32", "«internal timer»", w=2.3, h=1.1)
    draw_assoc_line(ax, (2.45, 4.3), p_main, ew, 'left')

    pt_dev = draw_device_actor(ax, 10.2, 4.3, "Module Relay 5V\n& Máy Bơm Mini", "«device»", w=2.4, h=1.1)
    draw_assoc_line(ax, (9.0, 4.3), p_main, ew, 'right')

    # Include from parent to both children
    draw_include(ax, (p_main[0], p_main[1] - 0.41), (p_on[0], p_on[1] + 0.39))
    draw_include(ax, (p_main[0] - 1.2, p_main[1] - 0.41), (p_off[0] - 1.2, p_off[1] + 0.39))

    save_fig(fig, "uc03_pump_control.png")


# =============================================================
# 5. UC04: Tự Động Điều Khiển Van Thoát Lũ (Proper «include»)
# =============================================================
def make_uc04_bw():
    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 5.8, 5.2, 
                       "Phân Hệ Điều Khiển Van Lũ (ESP32 Firmware)")

    ew = 4.8
    eh = 0.82
    p_main = draw_ellipse(ax, 5.6, 4.3, ew, eh, "UC04: Tự Động Điều Khiển Van Lũ")
    p_mid  = draw_ellipse(ax, 5.6, 2.8, 4.8, 0.78, "Xuất PWM Mở Van 50% Góc 90° (DANGER)")
    p_full = draw_ellipse(ax, 5.6, 1.3, 4.8, 0.78, "Xuất PWM Mở Van 100% Góc 180° (CRITICAL)")

    pt_tm = draw_timer_actor(ax, 1.3, 4.3, "Trình Điều Phối\nFSM ESP32", "«internal timer»", w=2.3, h=1.1)
    draw_assoc_line(ax, (2.45, 4.3), p_main, ew, 'left')

    pt_dev = draw_device_actor(ax, 10.2, 4.3, "Động Cơ Servo\nSG90 (GPIO 27)", "«device»", w=2.4, h=1.1)
    draw_assoc_line(ax, (9.0, 4.3), p_main, ew, 'right')

    # Include from parent to both children
    draw_include(ax, (p_main[0], p_main[1] - 0.41), (p_mid[0], p_mid[1] + 0.39))
    draw_include(ax, (p_main[0] - 1.2, p_main[1] - 0.41), (p_full[0] - 1.2, p_full[1] + 0.39))

    save_fig(fig, "uc04_valve_control.png")


# =============================================================
# 6. UC05: Cảnh Báo LED & Còi Buzzer (Proper «include»)
# =============================================================
def make_uc05_bw():
    fig, ax = plt.subplots(figsize=(12.0, 6.2), dpi=300)
    ax.set_xlim(0, 12.0)
    ax.set_ylim(0, 6.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 6.0, 5.2, 
                       "Phân Hệ Cảnh Báo Tại Chỗ (ESP32 Firmware)")

    ew = 4.8
    eh = 0.82
    p_main = draw_ellipse(ax, 5.7, 4.3, ew, eh, "UC05: Phát Cảnh Báo LED & Còi")
    p_led  = draw_ellipse(ax, 5.7, 2.8, 4.8, 0.78, "Chỉ Thị LED Trực Quan (Xanh/Vàng/Đỏ)")
    p_buz  = draw_ellipse(ax, 5.7, 1.3, 4.8, 0.78, "Kích Âm Còi Non-blocking (millis)")

    pt_tm = draw_timer_actor(ax, 1.3, 4.3, "Trình Điều Phối\nFSM ESP32", "«internal timer»", w=2.3, h=1.1)
    draw_assoc_line(ax, (2.45, 4.3), p_main, ew, 'left')

    pt_dev = draw_device_actor(ax, 10.5, 4.8, "Cụm 3 Đèn LED\n& Còi Buzzer 5V", "«device»", w=2.4, h=1.1)
    draw_assoc_line(ax, (9.3, 4.8), p_main, ew, 'right')

    pt_res = draw_human_actor(ax, 10.5, 2.0, "Người Dân\nQuanh Trạm", "«human actor»", scale=0.88)
    draw_assoc_line(ax, (9.6, 2.4), p_main, ew, 'right')

    draw_include(ax, (p_main[0], p_main[1] - 0.41), (p_led[0], p_led[1] + 0.39))
    draw_include(ax, (p_main[0] - 1.2, p_main[1] - 0.41), (p_buz[0] - 1.2, p_buz[1] + 0.39))

    save_fig(fig, "uc05_signaling_buzzer_led.png")


# =============================================================
# 7. UC06: Failsafe to AUTO (Proper «include»)
# Actor: Watchdog Timer triggers, Operator receives notification/impact
# =============================================================
def make_uc06_bw():
    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 5.8, 5.2, 
                       "Phân Hệ Tự Trị Failsafe (ESP32 Firmware)")

    ew = 4.8
    eh = 0.82
    p_main = draw_ellipse(ax, 5.6, 4.3, ew, eh, "UC06: Tự Động Chuyển Về AUTO")
    p_chk  = draw_ellipse(ax, 5.6, 2.8, 4.8, 0.78, "Kiểm Tra Timeout Kết Nối Wi-Fi / Web")
    p_fsm  = draw_ellipse(ax, 5.6, 1.3, 4.8, 0.78, "Cưỡng Chế Đảo Cờ isAutoMode = true")

    # Watchdog Timer is the primary triggering actor
    pt_wd = draw_timer_actor(ax, 1.3, 4.3, "Bộ Giám Sát\nWatchdog / Timeout", "«internal timer»", w=2.4, h=1.1)
    draw_assoc_line(ax, (2.5, 4.3), p_main, ew, 'left')

    # Human operator is the secondary affected party (lost control)
    pt_op = draw_human_actor(ax, 10.2, 4.0, "Người Vận Hành\n(Mất Kết Nối)", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (9.3, 4.3), p_main, ew, 'right')

    draw_include(ax, (p_main[0], p_main[1] - 0.41), (p_chk[0], p_chk[1] + 0.39))
    draw_include(ax, (p_main[0] - 1.2, p_main[1] - 0.41), (p_fsm[0] - 1.2, p_fsm[1] + 0.39))

    save_fig(fig, "uc06_network_failsafe.png")


# =============================================================
# 8. UC07: Truyền Nhận Telemetry & API (Proper «include»)
# =============================================================
def make_uc07_bw():
    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 5.8, 5.2, 
                       "Phân Hệ Web Server & REST API (ESP32)")

    ew = 4.8
    eh = 0.82
    p_main = draw_ellipse(ax, 5.6, 4.3, ew, eh, "UC07: Truyền Nhận Web API")
    p_stat = draw_ellipse(ax, 5.6, 2.8, 4.8, 0.78, "Đóng Gói Chuỗi JSON (GET /api/status)")
    p_cmd  = draw_ellipse(ax, 5.6, 1.3, 4.8, 0.78, "Tiếp Nhận Gói Lệnh (GET /api/control)")

    pt_op = draw_human_actor(ax, 1.3, 4.0, "Người Vận Hành", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (2.2, 4.3), p_main, ew, 'left')

    pt_srv = draw_device_actor(ax, 10.2, 4.3, "ESP32 Web Server\n(Port 80 HTTP)", "«server»", w=2.4, h=1.1)
    draw_assoc_line(ax, (9.0, 4.3), p_main, ew, 'right')

    draw_include(ax, (p_main[0], p_main[1] - 0.41), (p_stat[0], p_stat[1] + 0.39))
    draw_include(ax, (p_main[0] - 1.2, p_main[1] - 0.41), (p_cmd[0] - 1.2, p_cmd[1] + 0.39))

    save_fig(fig, "uc07_telemetry_api.png")


# =============================================================
# 9. UC08: Giám Sát Web Dashboard (Proper «include»)
# =============================================================
def make_uc08_bw():
    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 5.8, 5.2, 
                       "Phân Hệ Web Dashboard (ESP32 Web App)")

    ew = 4.8
    eh = 0.82
    p_main = draw_ellipse(ax, 5.6, 4.3, ew, eh, "UC08: Giám Sát Trạng Thái Web")
    p_bar  = draw_ellipse(ax, 5.6, 2.8, 4.8, 0.78, "Hiển Thị Đồng Hồ Mực Nước % & Khoảng Cách")
    p_dev  = draw_ellipse(ax, 5.6, 1.3, 4.8, 0.78, "Cập Nhật Trạng Thái Bơm, Van Xả & Còi")

    pt_op = draw_human_actor(ax, 1.3, 4.0, "Người Vận Hành", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (2.2, 4.3), p_main, ew, 'left')

    draw_include(ax, (p_main[0], p_main[1] - 0.41), (p_bar[0], p_bar[1] + 0.39))
    draw_include(ax, (p_main[0] - 1.2, p_main[1] - 0.41), (p_dev[0] - 1.2, p_dev[1] + 0.39))

    save_fig(fig, "uc08_web_dashboard.png")


# =============================================================
# 10. UC09: Chuyển Đổi AUTO/MANUAL (Strict UML «extend»)
# Both branches point BACK to Base UC09. Arrows point UPWARD.
# =============================================================
def make_uc09_bw():
    fig, ax = plt.subplots(figsize=(11.5, 6.5), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 6.0, 5.5, 
                       "Phân Hệ Quản Lý Chế Độ (ESP32 Firmware)")

    ew = 4.8
    eh = 0.82
    # Base Use Case
    p_main = draw_ellipse(ax, 5.7, 4.6, ew, eh, "UC09: Chuyển Đổi Chế Độ Vận Hành")
    
    # Extension Use Cases (independent branches)
    p_auto = draw_ellipse(ax, 5.7, 2.8, 5.2, 0.78, "Khóa Phím Web, Giao Quyền Tự Động Cho FSM")
    p_manu = draw_ellipse(ax, 5.7, 1.2, 5.2, 0.78, "Mở Khóa Nút Bấm, Cho Phép Can Thiệp Thủ Công")

    pt_op = draw_human_actor(ax, 1.3, 4.3, "Người Vận Hành", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (2.2, 4.6), p_main, ew, 'left')

    # Strict UML: Arrows point from Extension UC to Base UC
    draw_extend(ax, (p_auto[0] - 0.8, p_auto[1] + 0.39), (p_main[0] - 0.8, p_main[1] - 0.41), "«extend» [khi chọn AUTO]")
    draw_extend(ax, (p_manu[0] + 0.8, p_manu[1] + 0.39), (p_main[0] + 0.8, p_main[1] - 0.41), "«extend» [khi chọn MANUAL]")

    save_fig(fig, "uc09_mode_switch.png")


# =============================================================
# 11. UC10: Can Thiệp Cưỡng Chế Thiết Bị (Strict UML «extend»)
# Both branches point BACK to Base UC10. Secondary devices attached.
# =============================================================
def make_uc10_bw():
    fig, ax = plt.subplots(figsize=(12.0, 6.5), dpi=300)
    ax.set_xlim(0, 12.0)
    ax.set_ylim(0, 6.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 6.2, 5.5, 
                       "Phân Hệ Can Thiệp Cưỡng Chế (ESP32 Firmware)")

    ew = 5.0
    eh = 0.82
    # Base Use Case
    p_main = draw_ellipse(ax, 5.8, 4.6, ew, eh, "UC10: Can Thiệp Cưỡng Chế Thiết Bị")
    
    # Extension Use Cases (independent override branches)
    p_pump = draw_ellipse(ax, 5.8, 2.8, 5.2, 0.78, "Bật / Tắt Cưỡng Chế Máy Bơm Thoát Nước")
    p_gate = draw_ellipse(ax, 5.8, 1.2, 5.2, 0.78, "Điều Khiển Cưỡng Chế Góc Van Xả (0°/90°/180°)")

    pt_op = draw_human_actor(ax, 1.3, 4.3, "Người Vận Hành", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (2.2, 4.6), p_main, ew, 'left')

    pt_pump = draw_device_actor(ax, 10.6, 2.8, "Module Relay 5V\n& Máy Bơm Mini", "«device»", w=2.4, h=1.1)
    draw_assoc_line(ax, (9.4, 2.8), p_pump, 5.2, 'right')

    pt_servo = draw_device_actor(ax, 10.6, 1.2, "Động Cơ Servo\nSG90 (Van Lũ)", "«device»", w=2.4, h=1.1)
    draw_assoc_line(ax, (9.4, 1.2), p_gate, 5.2, 'right')

    # Strict UML: Arrows point from Extension UC back to Base UC
    draw_extend(ax, (p_pump[0] - 0.8, p_pump[1] + 0.39), (p_main[0] - 0.8, p_main[1] - 0.41), "«extend» [khi lệnh Bơm]")
    draw_extend(ax, (p_gate[0] + 0.8, p_gate[1] + 0.39), (p_main[0] + 0.8, p_main[1] - 0.41), "«extend» [khi lệnh Van]")

    save_fig(fig, "uc10_manual_override.png")


if __name__ == "__main__":
    print("Generating pure black & white UML Use Case diagrams with strict UML 2.5 standards...")
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
