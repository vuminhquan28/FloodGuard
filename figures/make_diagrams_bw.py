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

# Set high quality font & line styling
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#000000'
plt.rcParams['axes.linewidth'] = 1.4
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
    print(f"Generated UML Diagram: {filename}")

def get_ellipse_border(xc, yc, w, h, target_x, target_y):
    """
    Computes exact mathematical point on the boundary of an ellipse
    centered at (xc, yc) with width w and height h along the ray toward (target_x, target_y).
    """
    a = w / 2.0
    b = h / 2.0
    dx = target_x - xc
    dy = target_y - yc
    if dx == 0 and dy == 0:
        return float(xc), float(yc)
    theta = np.arctan2(dy, dx)
    t = 1.0 / np.sqrt((np.cos(theta)/a)**2 + (np.sin(theta)/b)**2)
    return float(xc + t * np.cos(theta)), float(yc + t * np.sin(theta))

def draw_human_actor(ax, x, y, label, sublabel="«human actor»", scale=1.15):
    """Draws a standard UML human actor stick figure with clear large text"""
    r = 0.26 * scale
    head = plt.Circle((x, y + 0.44 * scale), r, facecolor='#ffffff', edgecolor='#000000', lw=1.6, zorder=6)
    ax.add_patch(head)
    # Body
    ax.plot([x, x], [y + 0.18 * scale, y - 0.38 * scale], color='#000000', lw=1.8, zorder=6)
    # Arms
    ax.plot([x - 0.34 * scale, x + 0.34 * scale], [y - 0.02 * scale, y - 0.02 * scale], color='#000000', lw=1.8, zorder=6)
    # Legs
    ax.plot([x, x - 0.28 * scale], [y - 0.38 * scale, y - 0.85 * scale], color='#000000', lw=1.8, zorder=6)
    ax.plot([x, x + 0.28 * scale], [y - 0.38 * scale, y - 0.85 * scale], color='#000000', lw=1.8, zorder=6)
    # Label
    ax.text(x, y - 1.05 * scale, label, fontsize=11.0, fontweight='bold', ha='center', va='top', color='#000000')
    if sublabel:
        ax.text(x, y - 1.50 * scale, sublabel, fontsize=9.5, style='italic', ha='center', va='top', color='#333333')
    return (x, y - 0.02 * scale)

def draw_device_actor(ax, x, y, label, sublabel="«device»", w=2.8, h=1.25):
    """Draws a standard UML device actor box with clear large text"""
    rect = patches.Rectangle((x - w/2, y - h/2), w, h, linewidth=1.6, edgecolor='#000000', facecolor='#ffffff', zorder=6)
    ax.add_patch(rect)
    ax.text(x, y + 0.28, sublabel, fontsize=9.5, style='italic', ha='center', va='center', color='#000000', zorder=7)
    ax.text(x, y - 0.18, label, fontsize=10.5, fontweight='bold', ha='center', va='center', color='#000000', zorder=7)
    return (x, y)

def draw_timer_actor(ax, x, y, label="Bộ Định Thời Timer", sublabel="«internal timer»", w=2.8, h=1.25):
    """Draws an internal timer / clock trigger actor"""
    rect = patches.Rectangle((x - w/2, y - h/2), w, h, linewidth=1.6, edgecolor='#000000', facecolor='#ffffff', zorder=6)
    ax.add_patch(rect)
    ax.text(x, y + 0.28, sublabel, fontsize=9.5, style='italic', ha='center', va='center', color='#000000', zorder=7)
    ax.text(x, y - 0.18, label, fontsize=10.5, fontweight='bold', ha='center', va='center', color='#000000', zorder=7)
    return (x, y)

def draw_subsystem_box(ax, x, y, w, h, title):
    rect = patches.Rectangle((x, y), w, h, linewidth=1.8, edgecolor='#000000', facecolor='#ffffff', zorder=1)
    ax.add_patch(rect)
    ax.text(x + 0.3, y + h - 0.40, "«system boundary»", fontsize=10.0, style='italic', color='#444444')
    ax.text(x + 0.3, y + h - 0.85, title, fontsize=12.5, fontweight='bold', color='#000000')

def draw_ellipse(ax, x, y, w, h, text, fontsize=10.5):
    ellipse = patches.Ellipse((x, y), w, h, facecolor='#ffffff', edgecolor='#000000', lw=1.5, zorder=3)
    ax.add_patch(ellipse)
    ax.text(x, y, text, fontsize=fontsize, fontweight='bold', ha='center', va='center', color='#000000', zorder=4)
    return (x, y, w, h)

def draw_assoc_line(ax, pt_from, e_to):
    """Solid association line between actor and exact ellipse border"""
    xc, yc, w, h = e_to
    pt_target = get_ellipse_border(xc, yc, w, h, pt_from[0], pt_from[1])
    ax.plot([pt_from[0], pt_target[0]], [pt_from[1], pt_target[1]], color='#000000', lw=1.3, zorder=2)

def draw_include(ax, e_from, e_to, label="«include»"):
    """Dashed arrow from Parent UC to Child UC, label placed cleanly above"""
    p_from = get_ellipse_border(e_from[0], e_from[1], e_from[2], e_from[3], e_to[0], e_to[1])
    p_to   = get_ellipse_border(e_to[0], e_to[1], e_to[2], e_to[3], e_from[0], e_from[1])

    ax.annotate("", xy=p_to, xytext=p_from,
                arrowprops=dict(arrowstyle="->", lw=1.4, linestyle="--", color="#000000",
                                shrinkA=0, shrinkB=0), zorder=4)

    dx = p_to[0] - p_from[0]
    dy = p_to[1] - p_from[1]
    L = np.hypot(dx, dy)
    if L == 0:
        return
    angle = np.degrees(np.arctan2(dy, dx))
    nx, ny = -dy / L, dx / L
    offset = 0.24
    tx = (p_from[0] + p_to[0]) / 2.0 + offset * nx
    ty = (p_from[1] + p_to[1]) / 2.0 + offset * ny

    ax.text(tx, ty, label, fontsize=10.0, style='italic', color='#000000',
            rotation=angle, rotation_mode='anchor',
            ha='center', va='bottom', zorder=6)

def draw_extend(ax, e_from, e_to, label="«extend»"):
    """Dashed arrow from Extension UC to Base UC"""
    p_from = get_ellipse_border(e_from[0], e_from[1], e_from[2], e_from[3], e_to[0], e_to[1])
    p_to   = get_ellipse_border(e_to[0], e_to[1], e_to[2], e_to[3], e_from[0], e_from[1])

    ax.annotate("", xy=p_to, xytext=p_from,
                arrowprops=dict(arrowstyle="->", lw=1.4, linestyle="--", color="#000000",
                                shrinkA=0, shrinkB=0), zorder=4)

    dx = p_to[0] - p_from[0]
    dy = p_to[1] - p_from[1]
    L = np.hypot(dx, dy)
    if L == 0:
        return
    mx = (p_from[0] + p_to[0]) / 2.0
    my = (p_from[1] + p_to[1]) / 2.0

    if dx >= 0:
        tx = mx - 0.3
        ty = my + 0.12
        ha = 'right'
    else:
        tx = mx + 0.3
        ty = my + 0.12
        ha = 'left'

    ax.text(tx, ty, label, fontsize=10.0, style='italic', color='#000000',
            ha=ha, va='center', zorder=6)

def draw_generalization(ax, e_from, e_to, label=""):
    """
    Standard UML Generalization:
    Solid line from child (e_from) with a closed hollow triangle arrowhead at parent (e_to).
    """
    p_from = get_ellipse_border(e_from[0], e_from[1], e_from[2], e_from[3], e_to[0], e_to[1])
    p_to   = get_ellipse_border(e_to[0], e_to[1], e_to[2], e_to[3], e_from[0], e_from[1])

    dx = p_to[0] - p_from[0]
    dy = p_to[1] - p_from[1]
    L = np.hypot(dx, dy)
    if L == 0:
        return
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux

    tri_len = 0.42
    tri_w = 0.26

    bx = p_to[0] - tri_len * ux
    by = p_to[1] - tri_len * uy

    v1 = (bx + tri_w * nx, by + tri_w * ny)
    v2 = (bx - tri_w * nx, by - tri_w * ny)

    # Line from child border to base of triangle
    ax.plot([p_from[0], bx], [p_from[1], by], color='#000000', lw=1.4, zorder=4)

    # Hollow triangle at parent end
    tri = patches.Polygon([p_to, v1, v2], closed=True, facecolor='#ffffff', edgecolor='#000000', lw=1.4, zorder=5)
    ax.add_patch(tri)

    if label:
        offset = 0.25
        tx = (p_from[0] + bx) / 2.0 + offset * nx
        ty = (p_from[1] + by) / 2.0 + offset * ny
        angle = np.degrees(np.arctan2(dy, dx))
        ax.text(tx, ty, label, fontsize=9.5, style='italic', color='#000000',
                rotation=angle, rotation_mode='anchor', ha='center', va='bottom', zorder=6)


# =============================================================
# 1. OVERALL SYSTEM USE CASE DIAGRAM
# Clean actors separation: Primary on Left, Secondary on Right.
# UC10 connects directly to Pump & Servo actuators (No phantom actor).
# =============================================================
def make_overall_uml_bw():
    fig, ax = plt.subplots(figsize=(16.8, 14.0), dpi=300)
    ax.set_xlim(0, 16.8)
    ax.set_ylim(0, 14.0)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # System Boundary Box
    rect = patches.FancyBboxPatch((3.4, 0.4), 9.9, 13.2, boxstyle='round,pad=0.0,rounding_size=0.18',
                                  linewidth=1.8, edgecolor='#000000', facecolor='#ffffff', zorder=1)
    ax.add_patch(rect)
    ax.text(3.7, 13.35, '«system boundary»', fontsize=9.5, style='italic', color='#555555', zorder=5)
    ax.text(3.7, 12.95, 'Hệ Thống Trạm FloodGuard (FloodGuard System)', fontsize=12.5, fontweight='bold', color='#000000', zorder=5)

    # Subsystem 1 Box: Autonomous Core
    box1 = patches.FancyBboxPatch((3.7, 5.3), 9.3, 7.35, boxstyle='round,pad=0.0,rounding_size=0.12',
                                  linewidth=1.2, linestyle='--', edgecolor='#555555', facecolor='#fafafa', zorder=2)
    ax.add_patch(box1)
    ax.text(4.0, 12.4, '«subsystem» Phân Hệ Giám Sát & Điều Khiển Tự Động Tại Chỗ', fontsize=10.0, fontweight='bold', color='#222222', zorder=5)

    # Subsystem 2 Box: Remote Telemetry & Web
    box2 = patches.FancyBboxPatch((3.7, 0.6), 9.3, 4.45, boxstyle='round,pad=0.0,rounding_size=0.12',
                                  linewidth=1.2, linestyle='--', edgecolor='#555555', facecolor='#fafafa', zorder=2)
    ax.add_patch(box2)
    ax.text(4.0, 4.8, '«subsystem» Phân Hệ Giám Sát & Điều Khiển Từ Xa Qua Web', fontsize=10.0, fontweight='bold', color='#222222', zorder=5)

    uc_list = [
        ('UC01: Đọc & Tiền Xử Lý Dữ Liệu Cảm Biến', 11.6),
        ('UC02: Tự Động Đánh Giá FSM & Dải Trễ', 10.4),
        ('UC03: Tự Động Điều Khiển Máy Bơm Thoát Nước', 9.2),
        ('UC04: Tự Động Điều Khiển Van Thoát Lũ', 8.0),
        ('UC05: Phát Tín Hiệu Cảnh Báo Tại Trạm', 6.8),
        ('UC06: Tự Động Chuyển An Toàn (Failsafe)', 5.7),
        ('UC07: Truyền Nhận Dữ Liệu Qua Web API', 4.1),
        ('UC08: Giám Sát Trạng Thái Trạm Qua Web', 3.0),
        ('UC09: Chuyển Đổi Chế Độ (AUTO / MANUAL)', 1.9),
        ('UC10: Can Thiệp Điều Khiển Thiết Bị Từ Web', 0.9)
    ]

    ew = 6.4
    eh = 0.82
    cx = 8.35
    uc_pos = {}

    for name, cy in uc_list:
        e = patches.Ellipse((cx, cy), ew, eh, facecolor='#ffffff', edgecolor='#000000', lw=1.4, zorder=3)
        ax.add_patch(e)
        ax.text(cx, cy, name, fontsize=10.0, fontweight='bold', ha='center', va='center', color='#000000', zorder=4)
        uc_pos[name[:4]] = cy

    # ACTORS
    # 1. Timer Actor (Top Left)
    rect_t = patches.Rectangle((0.3, 8.8), 2.5, 1.25, linewidth=1.4, edgecolor='#000000', facecolor='#ffffff', zorder=6)
    ax.add_patch(rect_t)
    ax.text(1.55, 9.65, '«internal timer»', fontsize=8.5, style='italic', ha='center', va='center', zorder=7)
    ax.text(1.55, 9.25, 'Bộ Định Thời\nTimer / Watchdog', fontsize=9.5, fontweight='bold', ha='center', va='center', zorder=7)

    # Timer Bus: spine at x=4.2
    ax.plot([2.8, 4.2], [9.4, 9.4], color='#000000', lw=1.3, zorder=2)
    ax.plot([4.2, 4.2], [5.7, 11.6], color='#000000', lw=1.3, zorder=2)
    for ucid in ['UC01', 'UC02', 'UC03', 'UC04', 'UC05', 'UC06']:
        y = uc_pos[ucid]
        ax.plot([4.2, cx - ew/2], [y, y], color='#000000', lw=1.3, zorder=2)

    # 2. Operator Actor (Bottom Left)
    scale = 0.85
    oy = 2.5
    ox = 1.55
    r = 0.24 * scale
    head = plt.Circle((ox, oy + 0.44 * scale), r, facecolor='#ffffff', edgecolor='#000000', lw=1.5, zorder=6)
    ax.add_patch(head)
    ax.plot([ox, ox], [oy + 0.18 * scale, oy - 0.38 * scale], color='#000000', lw=1.6, zorder=6)
    ax.plot([ox - 0.32 * scale, ox + 0.32 * scale], [oy - 0.02 * scale, oy - 0.02 * scale], color='#000000', lw=1.6, zorder=6)
    ax.plot([ox, ox - 0.26 * scale], [oy - 0.38 * scale, oy - 0.82 * scale], color='#000000', lw=1.6, zorder=6)
    ax.plot([ox, ox + 0.26 * scale], [oy - 0.38 * scale, oy - 0.82 * scale], color='#000000', lw=1.6, zorder=6)
    ax.text(ox, oy - 1.0 * scale, 'Người Vận Hành\n(Trình Duyệt Web)', fontsize=9.5, fontweight='bold', ha='center', va='top', zorder=7)
    ax.text(ox, oy - 1.45 * scale, '«human actor»', fontsize=8.5, style='italic', ha='center', va='top', color='#333333', zorder=7)

    # Operator direct lines
    for ucid in ['UC07', 'UC08', 'UC09', 'UC10']:
        y = uc_pos[ucid]
        ax.plot([2.55, cx - ew/2], [oy, y], color='#000000', lw=1.3, zorder=2)

    # RIGHT ACTORS
    # 3. Sensors (y=11.6)
    rect_s = patches.Rectangle((13.9, 11.0), 2.6, 1.2, linewidth=1.4, edgecolor='#000000', facecolor='#ffffff', zorder=6)
    ax.add_patch(rect_s)
    ax.text(15.2, 11.75, '«device»', fontsize=8.5, style='italic', ha='center', va='center', zorder=7)
    ax.text(15.2, 11.35, 'Cảm Biến Siêu Âm\n& Cảm Biến Mưa', fontsize=9.5, fontweight='bold', ha='center', va='center', zorder=7)
    ax.plot([cx + ew/2, 13.9], [11.6, 11.6], color='#000000', lw=1.3, zorder=2)

    # 4. Pump Relay (y=9.8)
    rect_p = patches.Rectangle((13.9, 9.25), 2.6, 1.15, linewidth=1.4, edgecolor='#000000', facecolor='#ffffff', zorder=6)
    ax.add_patch(rect_p)
    ax.text(15.2, 9.95, '«device»', fontsize=8.5, style='italic', ha='center', va='center', zorder=7)
    ax.text(15.2, 9.6, 'Module Relay 5V\n& Máy Bơm Mini', fontsize=9.5, fontweight='bold', ha='center', va='center', zorder=7)
    ax.plot([cx + ew/2, 13.9], [9.2, 9.5], color='#000000', lw=1.3, zorder=2)

    # 5. Servo Gate (y=8.3)
    rect_v = patches.Rectangle((13.9, 7.95), 2.6, 1.15, linewidth=1.4, edgecolor='#000000', facecolor='#ffffff', zorder=6)
    ax.add_patch(rect_v)
    ax.text(15.2, 8.65, '«device»', fontsize=8.5, style='italic', ha='center', va='center', zorder=7)
    ax.text(15.2, 8.3, 'Động Cơ Servo\nSG90 (Cửa Van)', fontsize=9.5, fontweight='bold', ha='center', va='center', zorder=7)
    ax.plot([cx + ew/2, 13.9], [8.0, 8.2], color='#000000', lw=1.3, zorder=2)

    # 6. LED & Buzzer (y=6.9)
    rect_l = patches.Rectangle((13.9, 6.65), 2.6, 1.15, linewidth=1.4, edgecolor='#000000', facecolor='#ffffff', zorder=6)
    ax.add_patch(rect_l)
    ax.text(15.2, 7.35, '«device»', fontsize=8.5, style='italic', ha='center', va='center', zorder=7)
    ax.text(15.2, 7.0, 'Cụm 3 Đèn LED\n& Còi Buzzer 5V', fontsize=9.5, fontweight='bold', ha='center', va='center', zorder=7)
    ax.plot([cx + ew/2, 13.9], [6.8, 6.95], color='#000000', lw=1.3, zorder=2)

    # 7. Residents (y=5.5)
    ry = 5.45
    rx = 15.2
    head2 = plt.Circle((rx, ry + 0.44 * scale), r, facecolor='#ffffff', edgecolor='#000000', lw=1.5, zorder=6)
    ax.add_patch(head2)
    ax.plot([rx, rx], [ry + 0.18 * scale, ry - 0.38 * scale], color='#000000', lw=1.6, zorder=6)
    ax.plot([rx - 0.32 * scale, rx + 0.32 * scale], [ry - 0.02 * scale, ry - 0.02 * scale], color='#000000', lw=1.6, zorder=6)
    ax.plot([rx, rx - 0.26 * scale], [ry - 0.38 * scale, ry - 0.82 * scale], color='#000000', lw=1.6, zorder=6)
    ax.plot([rx, rx + 0.26 * scale], [ry - 0.38 * scale, ry - 0.82 * scale], color='#000000', lw=1.6, zorder=6)
    ax.text(rx, ry - 1.0 * scale, 'Người Dân\nQuanh Trạm', fontsize=9.5, fontweight='bold', ha='center', va='top', zorder=7)
    ax.text(rx, ry - 1.45 * scale, '«human actor»', fontsize=8.5, style='italic', ha='center', va='top', color='#333333', zorder=7)
    ax.plot([cx + ew/2, 14.3], [6.8, ry + 0.2], color='#000000', lw=1.3, zorder=2)

    # Bus from UC10 to Pump and Servo in right channel at x=12.4
    ax.plot([cx + ew/2, 12.4], [0.9, 0.9], color='#000000', lw=1.3, zorder=2)
    ax.plot([12.4, 12.4], [0.9, 9.5], color='#000000', lw=1.3, zorder=2)
    ax.plot([12.4, 13.9], [9.5, 9.5], color='#000000', lw=1.3, zorder=2) # to pump
    ax.plot([12.4, 13.9], [8.2, 8.2], color='#000000', lw=1.3, zorder=2) # to servo

    save_fig(fig, "uc_overall_diagram.png")


# =============================================================
# 2. UC01: Đọc & Tiền Xử Lý Dữ Liệu Cảm Biến
# =============================================================
def make_uc01_bw():
    fig, ax = plt.subplots(figsize=(15.5, 7.8), dpi=300)
    ax.set_xlim(0, 15.5)
    ax.set_ylim(0, 7.8)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 9.8, 6.8, 
                       "Phân Hệ Đo Đạc Cảm Biến (FloodGuard System)")

    e_main = draw_ellipse(ax, 5.0, 3.8, 3.8, 1.25, "UC01: Đọc & Tiền Xử Lý\nDữ Liệu Cảm Biến", fontsize=11.0)
    
    e_sub1 = draw_ellipse(ax, 10.2, 5.8, 4.4, 1.05, "Đo Khoảng Cách Siêu Âm\n(Kích Trig / Đo Echo)", fontsize=10.5)
    e_sub2 = draw_ellipse(ax, 10.2, 3.8, 4.4, 1.05, "Lọc Trung Vị 3 Mẫu &\nQuy Đổi % Mực Nước", fontsize=10.5)
    e_sub3 = draw_ellipse(ax, 10.2, 1.8, 4.4, 1.05, "Đọc Cảm Biến Mưa &\nPhân Cấp Tương Tự ADC/DO", fontsize=10.5)

    draw_timer_actor(ax, 1.3, 5.0, "Bộ Định Thời\nTimer 200ms", "«internal timer»", w=2.4, h=1.2)
    draw_assoc_line(ax, (2.5, 5.0), e_main)

    draw_device_actor(ax, 1.3, 2.6, "Cảm Biến HC-SR04\n& Cảm Biến Mưa", "«device»", w=2.4, h=1.2)
    draw_assoc_line(ax, (2.5, 2.6), e_main)

    draw_include(ax, e_main, e_sub1)
    draw_include(ax, e_main, e_sub2)
    draw_include(ax, e_main, e_sub3)

    save_fig(fig, "uc01_sensor_processing.png")


# =============================================================
# 3. UC02: Tự Động Đánh Giá FSM & Dải Trễ
# =============================================================
def make_uc02_bw():
    fig, ax = plt.subplots(figsize=(15.5, 7.8), dpi=300)
    ax.set_xlim(0, 15.5)
    ax.set_ylim(0, 7.8)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 9.8, 6.8, 
                       "Phân Hệ Logic FSM & Dải Trễ (FloodGuard System)")

    e_main = draw_ellipse(ax, 5.0, 3.8, 3.8, 1.25, "UC02: Tự Động Đánh Giá\nFSM & Dải Trễ", fontsize=11.0)
    
    e_sub1 = draw_ellipse(ax, 10.2, 5.2, 4.4, 1.15, "Đánh Giá 4 Cấp Độ FSM\n(NORMAL - CRITICAL)", fontsize=10.5)
    e_sub2 = draw_ellipse(ax, 10.2, 2.4, 4.4, 1.15, "Áp Dụng Dải Trễ Hysteresis\nChống Rung Giật (Chattering)", fontsize=10.5)

    draw_timer_actor(ax, 1.3, 3.8, "Bộ Định Thời\nChu Kỳ FSM", "«internal timer»", w=2.4, h=1.2)
    draw_assoc_line(ax, (2.5, 3.8), e_main)

    draw_include(ax, e_main, e_sub1)
    draw_include(ax, e_main, e_sub2)

    save_fig(fig, "uc02_fsm_hysteresis.png")


# =============================================================
# 4. UC03: Tự Động Điều Khiển Máy Bơm Thoát Nước (Generalization)
# Mutually exclusive: Bật Bơm vs Ngắt Bơm -> Generalization
# =============================================================
def make_uc03_bw():
    fig, ax = plt.subplots(figsize=(15.8, 8.0), dpi=300)
    ax.set_xlim(0, 15.8)
    ax.set_ylim(0, 8.0)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 9.8, 7.0, 
                       "Phân Hệ Điều Khiển Bơm Thoát Nước (FloodGuard System)")

    e_main = draw_ellipse(ax, 5.0, 4.0, 3.8, 1.25, "UC03: Tự Động Điều Khiển\nMáy Bơm Thoát Nước", fontsize=11.0)
    
    e_on  = draw_ellipse(ax, 10.2, 5.5, 4.4, 1.15, "Kích Relay Active LOW\n(Bật Bơm: DANGER / CRITICAL)", fontsize=10.5)
    e_off = draw_ellipse(ax, 10.2, 2.5, 4.4, 1.15, "Thả Nổi Relay High-Z\n(Ngắt Bơm: NORMAL / WARNING)", fontsize=10.5)

    # Primary Trigger is System Timer
    draw_timer_actor(ax, 1.3, 4.0, "Bộ Định Thời\nChu Kỳ FSM", "«internal timer»", w=2.4, h=1.2)
    draw_assoc_line(ax, (2.5, 4.0), e_main)

    # Secondary Device Actor
    draw_device_actor(ax, 14.2, 4.0, "Module Relay 5V\n& Máy Bơm Mini", "«device»", w=2.6, h=1.2)
    draw_assoc_line(ax, (12.9, 4.3), e_on)
    draw_assoc_line(ax, (12.9, 3.7), e_off)

    # Generalization arrows from specialized actions to UC03
    draw_generalization(ax, e_on, e_main)
    draw_generalization(ax, e_off, e_main)

    save_fig(fig, "uc03_pump_control.png")


# =============================================================
# 5. UC04: Tự Động Điều Khiển Van Thoát Lũ (Generalization)
# 3 mutually exclusive angles: 0°, 90°, 180° -> Generalization
# =============================================================
def make_uc04_bw():
    fig, ax = plt.subplots(figsize=(15.8, 8.2), dpi=300)
    ax.set_xlim(0, 15.8)
    ax.set_ylim(0, 8.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 9.8, 7.2, 
                       "Phân Hệ Điều Khiển Van Thoát Lũ (FloodGuard System)")

    e_main = draw_ellipse(ax, 5.0, 4.1, 3.8, 1.25, "UC04: Tự Động Điều Khiển\nVan Thoát Lũ", fontsize=11.0)
    
    e_close = draw_ellipse(ax, 10.2, 6.2, 4.4, 1.05, "Đóng Van Cửa Xả Góc 0°\n(NORMAL / WARNING)", fontsize=10.5)
    e_mid   = draw_ellipse(ax, 10.2, 4.1, 4.4, 1.05, "Mở Van Xả 50% Góc 90°\n(Mức DANGER)", fontsize=10.5)
    e_full  = draw_ellipse(ax, 10.2, 2.0, 4.4, 1.05, "Mở Van Xả 100% Góc 180°\n(Mức CRITICAL)", fontsize=10.5)

    # Primary Trigger is System Timer
    draw_timer_actor(ax, 1.3, 4.1, "Bộ Định Thời\nChu Kỳ FSM", "«internal timer»", w=2.4, h=1.2)
    draw_assoc_line(ax, (2.5, 4.1), e_main)

    # Secondary Device Actor
    draw_device_actor(ax, 14.2, 4.1, "Động Cơ Servo\nSG90 (Cửa Van)", "«device»", w=2.6, h=1.2)
    draw_assoc_line(ax, (12.9, 4.6), e_close)
    draw_assoc_line(ax, (12.9, 4.1), e_mid)
    draw_assoc_line(ax, (12.9, 3.6), e_full)

    # Generalization arrows
    draw_generalization(ax, e_close, e_main)
    draw_generalization(ax, e_mid, e_main)
    draw_generalization(ax, e_full, e_main)

    save_fig(fig, "uc04_valve_control.png")


# =============================================================
# 6. UC05: Cảnh Báo LED & Còi Buzzer Tại Trạm
# =============================================================
def make_uc05_bw():
    fig, ax = plt.subplots(figsize=(15.8, 8.0), dpi=300)
    ax.set_xlim(0, 15.8)
    ax.set_ylim(0, 8.0)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 9.8, 7.0, 
                       "Phân Hệ Cảnh Báo Tại Chỗ (FloodGuard System)")

    e_main = draw_ellipse(ax, 5.0, 4.0, 3.8, 1.25, "UC05: Phát Tín Hiệu\nCảnh Báo Tại Trạm", fontsize=11.0)
    
    e_led = draw_ellipse(ax, 10.2, 5.5, 4.4, 1.15, "Chỉ Thị Đèn LED Trực Quan\n(Xanh / Vàng / Đỏ)", fontsize=10.5)
    e_buz = draw_ellipse(ax, 10.2, 2.5, 4.4, 1.15, "Kích Âm Còi Báo Động\nNon-blocking (millis)", fontsize=10.5)

    # Primary Trigger
    draw_timer_actor(ax, 1.3, 4.0, "Bộ Định Thời\nChu Kỳ FSM", "«internal timer»", w=2.4, h=1.2)
    draw_assoc_line(ax, (2.5, 4.0), e_main)

    # Secondary Actors
    draw_device_actor(ax, 14.2, 5.5, "Cụm 3 Đèn LED\n& Còi Buzzer 5V", "«device»", w=2.6, h=1.2)
    draw_assoc_line(ax, (12.9, 5.5), e_led)
    draw_assoc_line(ax, (12.9, 4.8), e_buz)

    draw_human_actor(ax, 14.2, 2.2, "Người Dân\nQuanh Trạm", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (13.1, 2.5), e_buz)

    draw_include(ax, e_main, e_led)
    draw_include(ax, e_main, e_buz)

    save_fig(fig, "uc05_signaling_buzzer_led.png")


# =============================================================
# 7. UC06: Tự Động Chuyển An Toàn (Failsafe to AUTO)
# Operator receives notification only, NOT connected to internal check
# =============================================================
def make_uc06_bw():
    fig, ax = plt.subplots(figsize=(15.8, 8.0), dpi=300)
    ax.set_xlim(0, 15.8)
    ax.set_ylim(0, 8.0)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 9.8, 7.0, 
                       "Phân Hệ Giám Sát An Toàn Failsafe (FloodGuard System)")

    e_main = draw_ellipse(ax, 5.0, 4.0, 3.8, 1.25, "UC06: Tự Động Chuyển\nAn Toàn Về AUTO", fontsize=11.0)
    
    e_chk = draw_ellipse(ax, 10.2, 5.5, 4.4, 1.15, "Kiểm Tra Timeout Kết Nối\n(Heartbeat > 30s)", fontsize=10.5)
    e_fsm = draw_ellipse(ax, 10.2, 2.5, 4.4, 1.15, "Cưỡng Chế Đảo Cờ AUTO\n(isAutoMode = true)", fontsize=10.5)

    # Primary Trigger: Watchdog / Timer
    draw_timer_actor(ax, 1.3, 4.0, "Bộ Định Thời\nTimeout (30s)", "«internal timer»", w=2.4, h=1.2)
    draw_assoc_line(ax, (2.5, 4.0), e_main)

    # Secondary: Operator receives Failsafe Alert notification via Dashboard
    draw_human_actor(ax, 14.2, 4.0, "Người Vận Hành\n(Nhận Cảnh Báo)", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (13.1, 4.0), e_main)

    draw_include(ax, e_main, e_chk)
    draw_include(ax, e_main, e_fsm)

    save_fig(fig, "uc06_network_failsafe.png")


# =============================================================
# 8. UC07: Truyền Nhận Dữ Liệu Web API (Generalization)
# Removed internal Web Server actor! Primary is Human Operator via Browser.
# Two distinct request services: Telemetry Status vs Control Command.
# =============================================================
def make_uc07_bw():
    fig, ax = plt.subplots(figsize=(15.8, 8.0), dpi=300)
    ax.set_xlim(0, 15.8)
    ax.set_ylim(0, 8.0)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 11.2, 7.0, 
                       "Phân Hệ Dịch Vụ Web API (FloodGuard System)")

    e_main = draw_ellipse(ax, 5.2, 4.0, 4.0, 1.25, "UC07: Truyền Nhận\nDữ Liệu Web API", fontsize=11.0)
    
    e_stat = draw_ellipse(ax, 11.2, 5.5, 4.6, 1.15, "Đóng Gói Dữ Liệu JSON\n(GET /api/status)", fontsize=10.5)
    e_cmd  = draw_ellipse(ax, 11.2, 2.5, 4.6, 1.15, "Tiếp Nhận Gói Lệnh Can Thiệp\n(GET /api/control)", fontsize=10.5)

    # Primary Actor: Operator
    draw_human_actor(ax, 1.3, 4.0, "Người Vận Hành\n(Trình Duyệt Web)", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (2.3, 4.0), e_main)

    # Generalization: 2 distinct API request handlers specialized from UC07
    draw_generalization(ax, e_stat, e_main)
    draw_generalization(ax, e_cmd, e_main)

    save_fig(fig, "uc07_telemetry_api.png")


# =============================================================
# 9. UC08: Giám Sát Trạng Thái Trạm Qua Web Dashboard
# =============================================================
def make_uc08_bw():
    fig, ax = plt.subplots(figsize=(15.5, 7.8), dpi=300)
    ax.set_xlim(0, 15.5)
    ax.set_ylim(0, 7.8)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 9.8, 6.8, 
                       "Phân Hệ Web Dashboard (FloodGuard System)")

    e_main = draw_ellipse(ax, 5.0, 3.8, 3.8, 1.25, "UC08: Giám Sát Trạng Thái\nTrạm Qua Web Dashboard", fontsize=11.0)
    
    e_bar = draw_ellipse(ax, 10.2, 5.2, 4.4, 1.15, "Hiển Thị Đồng Hồ Mực Nước\n(% và Khoảng Cách cm)", fontsize=10.5)
    e_dev = draw_ellipse(ax, 10.2, 2.4, 4.4, 1.15, "Cập Nhật Trạng Thái Thiết Bị\n(Bơm, Van, LED, Còi)", fontsize=10.5)

    draw_human_actor(ax, 1.3, 3.8, "Người Vận Hành\n(Trình Duyệt Web)", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (2.3, 3.8), e_main)

    draw_include(ax, e_main, e_bar)
    draw_include(ax, e_main, e_dev)

    save_fig(fig, "uc08_web_dashboard.png")


# =============================================================
# 10. UC09: Chuyển Đổi Chế Độ Vận Hành (Generalization)
# Switching to AUTO vs switching to MANUAL are specializations of UC09
# =============================================================
def make_uc09_bw():
    fig, ax = plt.subplots(figsize=(15.5, 8.0), dpi=300)
    ax.set_xlim(0, 15.5)
    ax.set_ylim(0, 8.0)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 11.4, 7.0, 
                       "Phân Hệ Quản Lý Chế Độ Vận Hành (FloodGuard System)")

    # Base Use Case on Top Center
    e_main = draw_ellipse(ax, 8.6, 5.8, 5.0, 1.25, "UC09: Chuyển Đổi Chế Độ Vận Hành", fontsize=11.5)
    
    # 2 Specialized Children
    e_auto = draw_ellipse(ax, 5.8, 2.2, 4.4, 1.15, "Chuyển Sang Tự Động\n(Khóa Phím, Giao Quyền FSM)", fontsize=10.5)
    e_manu = draw_ellipse(ax, 11.4, 2.2, 4.4, 1.15, "Chuyển Sang Thủ Công\n(Mở Khóa Phím Can Thiệp)", fontsize=10.5)

    draw_human_actor(ax, 1.3, 5.8, "Người Vận Hành\n(Trình Duyệt Web)", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (2.3, 5.8), e_main)

    # Solid line with hollow triangle pointing up to UC09
    draw_generalization(ax, e_auto, e_main)
    draw_generalization(ax, e_manu, e_main)

    save_fig(fig, "uc09_mode_switch.png")


# =============================================================
# 11. UC10: Can Thiệp Điều Khiển Cưỡng Chế Thiết Bị Từ Web
# =============================================================
def make_uc10_bw():
    fig, ax = plt.subplots(figsize=(16.0, 8.0), dpi=300)
    ax.set_xlim(0, 16.0)
    ax.set_ylim(0, 8.0)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    draw_subsystem_box(ax, 2.8, 0.5, 10.2, 7.0, 
                       "Phân Hệ Can Thiệp Cưỡng Chế (FloodGuard System)")

    # Base Use Case on Top Center
    e_main = draw_ellipse(ax, 7.9, 5.8, 5.0, 1.25, "UC10: Can Thiệp Điều Khiển Thiết Bị Từ Web", fontsize=11.5)
    
    # 2 Extension Use Cases
    e_pump = draw_ellipse(ax, 5.4, 2.2, 4.0, 1.15, "Bật / Tắt Cưỡng Chế\nMáy Bơm Thoát Nước", fontsize=10.5)
    e_gate = draw_ellipse(ax, 10.4, 2.2, 4.0, 1.15, "Điều Khiển Cưỡng Chế\nGóc Van (0° / 90° / 180°)", fontsize=10.5)

    draw_human_actor(ax, 1.3, 5.8, "Người Vận Hành\n(Trình Duyệt Web)", "«human actor»", scale=0.9)
    draw_assoc_line(ax, (2.3, 5.8), e_main)

    draw_extend(ax, e_pump, e_main, "«extend»\n[lệnh Bơm]")
    draw_extend(ax, e_gate, e_main, "«extend»\n[lệnh Van]")

    # Actuator devices
    draw_device_actor(ax, 1.3, 2.2, "Module Relay 5V\n& Máy Bơm Mini", "«device»", w=2.6, h=1.2)
    draw_assoc_line(ax, (2.6, 2.2), e_pump)

    draw_device_actor(ax, 14.5, 2.2, "Động Cơ Servo\nSG90 (Cửa Van)", "«device»", w=2.6, h=1.2)
    draw_assoc_line(ax, (13.2, 2.2), e_gate)

    save_fig(fig, "uc10_manual_override.png")


if __name__ == "__main__":
    print("Generating strictly compliant UML diagrams with high readability & large fonts...")
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
