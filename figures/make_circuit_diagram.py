import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

out_paths = [
    os.path.join("d:\\1. project\\FloodGuard", "figures", "circuit_diagram.png"),
    os.path.join("d:\\1. project\\FloodGuard", "report", "figures", "circuit_diagram.png")
]
for p in out_paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['text.color'] = '#000000'


def draw_dot(ax, x, y, r=0.075):
    dot = plt.Circle((x, y), r, facecolor='#000000', edgecolor='#000000', zorder=12)
    ax.add_patch(dot)


def draw_wire(ax, pts, lw=1.8, ls='-', zorder=3):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs, ys, color='#000000', lw=lw, linestyle=ls, zorder=zorder,
            solid_capstyle='butt', solid_joinstyle='miter')


def draw_resistor_v(ax, x, yc, label="", val="", h=0.54, w=0.24, label_side='left', font_size=9.0):
    """IEC standard rectangular resistor vertical"""
    rect = patches.Rectangle((x - w/2, yc - h/2), w, h, facecolor='#ffffff',
                             edgecolor='#000000', lw=1.6, zorder=7)
    ax.add_patch(rect)
    if label or val:
        txt = f"{label}\n{val}".strip()
        if label_side == 'left':
            ax.text(x - w/2 - 0.08, yc, txt, fontsize=font_size, fontweight='bold', ha='right', va='center', zorder=10)
        else:
            ax.text(x + w/2 + 0.08, yc, txt, fontsize=font_size, fontweight='bold', ha='left', va='center', zorder=10)


def draw_resistor_h(ax, xc, y, label="", val="", w=0.62, h=0.25, font_size=9.8):
    """IEC standard rectangular resistor horizontal"""
    rect = patches.Rectangle((xc - w/2, y - h/2), w, h, facecolor='#ffffff',
                             edgecolor='#000000', lw=1.6, zorder=7)
    ax.add_patch(rect)
    if label or val:
        txt = f"{label} ({val})".strip()
        ax.text(xc, y + h/2 + 0.12, txt, fontsize=font_size, fontweight='bold', ha='center', va='bottom', zorder=10)


def draw_fuse_h(ax, xc, y, label="F1 (2A)", w=0.58, h=0.22, font_size=11.0):
    """IEC fuse symbol horizontal"""
    rect = patches.Rectangle((xc - w/2, y - h/2), w, h, facecolor='#ffffff',
                             edgecolor='#000000', lw=1.6, zorder=7)
    ax.add_patch(rect)
    ax.plot([xc - w/2 - 0.10, xc + w/2 + 0.10], [y, y], color='#000000', lw=1.6, zorder=8)
    ax.text(xc, y + h/2 + 0.14, label, fontsize=font_size, fontweight='bold', ha='center', va='bottom', zorder=10)


def draw_fuse_v(ax, x, yc, label="F2\n(1.5A)", h=0.60, w=0.24, font_size=10.0):
    """IEC fuse symbol vertical"""
    rect = patches.Rectangle((x - w/2, yc - h/2), w, h, facecolor='#ffffff',
                             edgecolor='#000000', lw=1.6, zorder=7)
    ax.add_patch(rect)
    ax.plot([x, x], [yc - h/2 - 0.10, yc + h/2 + 0.10], color='#000000', lw=1.6, zorder=8)
    ax.text(x + w/2 + 0.12, yc, label, fontsize=font_size, fontweight='bold', ha='left', va='center', zorder=10)


def draw_led_v(ax, x, yc, label="", font_size=9.0):
    """IEC LED symbol pointing down"""
    w = 0.36
    h = 0.32
    mask = patches.Rectangle((x - w/2 - 0.03, yc - h/2 - 0.03), w + 0.06, h + 0.06,
                             facecolor='#ffffff', edgecolor='none', zorder=6)
    ax.add_patch(mask)
    tri = patches.Polygon([[x - w/2, yc + h/2], [x + w/2, yc + h/2], [x, yc - h/2]],
                          closed=True, facecolor='#ffffff', edgecolor='#000000', lw=1.6, zorder=7)
    ax.add_patch(tri)
    ax.plot([x - w/2, x + w/2], [yc - h/2, yc - h/2], color='#000000', lw=2.0, zorder=8)
    # Emission arrows
    ax.annotate("", xy=(x + 0.38, yc - 0.04), xytext=(x + 0.20, yc + 0.14),
                arrowprops=dict(arrowstyle="->", lw=1.3, color='#000000'), zorder=9)
    ax.annotate("", xy=(x + 0.38, yc - 0.18), xytext=(x + 0.20, yc),
                arrowprops=dict(arrowstyle="->", lw=1.3, color='#000000'), zorder=9)
    if label:
        ax.text(x + 0.44, yc, label, fontsize=font_size, fontweight='bold', ha='left', va='center', zorder=10)


def draw_diode_up(ax, x, yc, label="D1", font_size=10.0):
    """Flyback diode pointing up"""
    w = 0.30
    h = 0.30
    mask = patches.Rectangle((x - w/2 - 0.03, yc - h/2 - 0.03), w + 0.06, h + 0.06,
                             facecolor='#ffffff', edgecolor='none', zorder=6)
    ax.add_patch(mask)
    tri = patches.Polygon([[x - w/2, yc - h/2], [x + w/2, yc - h/2], [x, yc + h/2]],
                          closed=True, facecolor='#ffffff', edgecolor='#000000', lw=1.6, zorder=7)
    ax.add_patch(tri)
    ax.plot([x - w/2, x + w/2], [yc + h/2, yc + h/2], color='#000000', lw=2.0, zorder=8)
    if label:
        ax.text(x - w/2 - 0.08, yc, label, fontsize=font_size, fontweight='bold', ha='right', va='center', zorder=10)


def draw_capacitor_v(ax, x, yc, label="C1\n220µF", font_size=10.5):
    """Polarized capacitor vertical with clean gap mask"""
    w = 0.46
    gap = 0.16
    mask = patches.Rectangle((x - w/2, yc - gap/2), w, gap, facecolor='#ffffff', edgecolor='none', zorder=6)
    ax.add_patch(mask)
    ax.plot([x - w/2, x + w/2], [yc + gap/2, yc + gap/2], color='#000000', lw=2.4, zorder=8)
    ax.plot([x - w/2, x + w/2], [yc - gap/2, yc - gap/2], color='#000000', lw=2.4, zorder=8)
    ax.text(x - w/2 - 0.08, yc + 0.18, "+", fontsize=12.0, fontweight='bold', ha='right', va='center', zorder=10)
    ax.text(x + w/2 + 0.10, yc, label, fontsize=font_size, fontweight='bold', ha='left', va='center', zorder=10)


def draw_switch_no_v(ax, x, yc, label="K1", h=0.60, font_size=12.0):
    """Normally Open (NO) contact vertical in IEC style"""
    mask = patches.Rectangle((x - 0.35, yc - h/2), 0.70, h, facecolor='#ffffff', edgecolor='none', zorder=6)
    ax.add_patch(mask)
    ax.plot([x, x - 0.28], [yc - h/2, yc + h/2 - 0.05], color='#000000', lw=2.2, zorder=8)
    draw_dot(ax, x, yc - h/2, r=0.07)
    draw_dot(ax, x, yc + h/2, r=0.07)
    ax.text(x + 0.22, yc, label, fontsize=font_size, fontweight='bold', ha='left', va='center', zorder=10)


def draw_switch_no_h(ax, xc, y, label="S1", w=0.52, font_size=11.0):
    """Normally Open (NO) switch horizontal"""
    mask = patches.Rectangle((xc - w/2, y - 0.32), w, 0.64, facecolor='#ffffff', edgecolor='none', zorder=6)
    ax.add_patch(mask)
    ax.plot([xc - w/2, xc + w/2 - 0.06], [y, y + 0.28], color='#000000', lw=2.2, zorder=8)
    draw_dot(ax, xc - w/2, y, r=0.07)
    draw_dot(ax, xc + w/2, y, r=0.07)
    ax.text(xc, y + 0.34, label, fontsize=font_size, fontweight='bold', ha='center', va='bottom', zorder=10)


def draw_group_box(ax, x, y, w, h, label="", badge_y=None, badge_fs=9.0):
    """Draw a clean dashed functional group bounding box with prominent title badge"""
    box = patches.Rectangle((x, y), w, h, facecolor='#ffffff', edgecolor='#000000',
                            lw=1.5, ls='--', zorder=2)
    ax.add_patch(box)
    if label:
        by = badge_y if badge_y is not None else (y + h)
        ax.text(x + w/2, by, label, fontsize=badge_fs, fontweight='bold',
                ha='center', va='center', color='#000000',
                bbox=dict(boxstyle="square,pad=0.25", facecolor='#ffffff', edgecolor='#000000', lw=1.3),
                zorder=9)


def create_circuit_diagram():
    # Canvas dimensions: 25.5 x 13.5 inches, high resolution 300 DPI
    fig, ax = plt.subplots(figsize=(25.5, 13.5), dpi=300)
    ax.set_xlim(0, 25.5)
    ax.set_ylim(0, 13.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Clean outer border
    border = patches.Rectangle((0.40, 0.40), 24.70, 12.70, facecolor='#ffffff', edgecolor='#000000', lw=1.8, zorder=1)
    ax.add_patch(border)

    # Header inside border
    ax.text(12.75, 12.65, "SƠ ĐỒ NGUYÊN LÝ MẠCH ĐIỆN VÀ PHÂN VÙNG CÁC KHỐI CHẤP HÀNH - FLOODGUARD",
            fontsize=17.5, fontweight='bold', ha='center', va='center', zorder=10)
    ax.text(12.75, 12.25, "Chuẩn ký hiệu IEC (Đơn sắc / Đen trắng): Khối Máy Tính  |  Khối Cảm Biến  |  Khối ESP32  |  Khối Cảnh Báo  |  Khối Van Xả  |  Khối Máy Bơm",
            fontsize=11.5, style='italic', ha='center', va='center', color='#222222', zorder=10)

    # ==========================================================
    # POWER RAILS
    # ==========================================================
    y_5v  = 11.20   # +5V rail
    y_gnd = 1.45    # Common GND rail

    # +5V Supply Entry (Top Left at x=0.55)
    ax.text(0.55, y_5v, "+5V DC\n(2A Nguồn)", fontsize=11.0, fontweight='bold', ha='left', va='center', zorder=10)
    draw_wire(ax, [(1.35, y_5v), (24.70, y_5v)], lw=2.2)
    draw_dot(ax, 1.35, y_5v, r=0.08)

    # Main Switch S1 at x=1.65 and Fuse F1 at x=2.40
    draw_switch_no_h(ax, 1.65, y_5v, label="S1", w=0.48, font_size=11.5)
    draw_fuse_h(ax, 2.40, y_5v, label="F1 (2A)", w=0.55, h=0.22, font_size=11.5)

    # Common GND Rail (Bottom)
    ax.text(0.55, y_gnd, "GND\n(Chung)", fontsize=11.0, fontweight='bold', ha='left', va='center', zorder=10)
    draw_wire(ax, [(1.35, y_gnd), (24.70, y_gnd)], lw=2.2)
    draw_dot(ax, 1.35, y_gnd, r=0.08)

    # Wire to HC-SR04 drops at x = 2.75 (AFTER F1 at x=2.40, cleanly to the LEFT of PC at x=3.10!)
    draw_dot(ax, 2.75, y_5v, r=0.08)
    draw_wire(ax, [(2.75, y_5v), (2.75, 5.65), (3.35, 5.65)])

    # ==========================================================
    # FUNCTIONAL GROUP 1: KHỐI MÁY TÍNH VẬN HÀNH (PC / LAPTOP)
    # Placed at x = [3.10, 6.70], y = [6.50, 10.10]
    # Monochrome B&W styling!
    # ==========================================================
    pc_x, pc_y, pc_w, pc_h = 3.10, 6.50, 3.60, 3.60
    draw_group_box(ax, pc_x, pc_y, pc_w, pc_h,
                   label="KHỐI MÁY TÍNH VẬN HÀNH\n(PC / LAPTOP)",
                   badge_y=pc_y + pc_h, badge_fs=9.0)

    # Laptop screen illustration inside (Clean B&W)
    scr_w, scr_h = 2.40, 1.45
    scr_x = pc_x + (pc_w - scr_w)/2
    scr_y = pc_y + 1.25
    scr_box = patches.Rectangle((scr_x, scr_y), scr_w, scr_h, facecolor='#ffffff', edgecolor='#000000', lw=1.6, zorder=5)
    ax.add_patch(scr_box)

    # Inner display
    disp = patches.Rectangle((scr_x + 0.10, scr_y + 0.10), scr_w - 0.20, scr_h - 0.20,
                             facecolor='#f6f7f8', edgecolor='#000000', lw=1.0, zorder=6)
    ax.add_patch(disp)
    ax.text(scr_x + scr_w/2, scr_y + scr_h/2 + 0.26, "WEB DASHBOARD", fontsize=9.5, fontweight='bold', ha='center', va='center', color='#000000', zorder=8)
    ax.text(scr_x + scr_w/2, scr_y + scr_h/2 - 0.04, "http://192.168.4.1", fontsize=9.0, fontweight='bold', ha='center', va='center', color='#000000', zorder=8)
    ax.text(scr_x + scr_w/2, scr_y + scr_h/2 - 0.34, "PlatformIO / Serial Monitor", fontsize=8.0, style='italic', ha='center', va='center', color='#333333', zorder=8)

    # Laptop base / keyboard
    base = patches.Polygon([[scr_x - 0.22, scr_y], [scr_x + scr_w + 0.22, scr_y],
                            [scr_x + scr_w + 0.36, scr_y - 0.22], [scr_x - 0.36, scr_y - 0.22]],
                           closed=True, facecolor='#ffffff', edgecolor='#000000', lw=1.6, zorder=6)
    ax.add_patch(base)

    # Subtitle inside laptop block
    ax.text(pc_x + pc_w/2, pc_y + 0.65, "Trạm giám sát Web qua Wi-Fi\n& Nạp code PlatformIO qua USB",
            fontsize=8.8, ha='center', va='center', color='#222222', zorder=8)

    # ==========================================================
    # FUNCTIONAL GROUP 2: KHỐI CẢM BIẾN ĐO ĐẠC (SENSORS)
    # Placed at x = [3.10, 6.70], y = [1.70, 6.25]
    # ==========================================================
    sns_x, sns_y, sns_w, sns_h = 3.10, 1.70, 3.60, 4.55
    draw_group_box(ax, sns_x, sns_y, sns_w, sns_h,
                   label="KHỐI CẢM BIẾN ĐO ĐẠC\n(SENSORS: HC-SR04 & FC-37)",
                   badge_y=sns_y + sns_h, badge_fs=9.0)

    # HC-SR04 Ultrasonic Sensor
    hc_x, hc_y, hc_w, hc_h = 3.35, 4.20, 3.10, 1.65
    hc_box = patches.Rectangle((hc_x, hc_y), hc_w, hc_h, facecolor='#ffffff', edgecolor='#000000', lw=1.8, zorder=4)
    ax.add_patch(hc_box)
    ax.text(hc_x + hc_w/2, hc_y + hc_h/2 + 0.22, "HC-SR04", fontsize=13.0, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(hc_x + hc_w/2, hc_y + hc_h/2 - 0.24, "(Cảm biến siêu âm đo mức nước)", fontsize=9.0, style='italic', ha='center', va='center', zorder=8)

    # HC-SR04 VCC pin label
    ax.text(hc_x + 0.14, 5.65, "VCC", fontsize=10.0, fontweight='bold', ha='left', va='center', zorder=8)

    # HC-SR04 GND -> GND rail (drops at x = 2.75)
    draw_wire(ax, [(hc_x, 4.45), (2.75, 4.45), (2.75, y_gnd)])
    draw_dot(ax, 2.75, y_gnd, r=0.08)
    ax.text(hc_x + 0.14, 4.45, "GND", fontsize=10.0, fontweight='bold', ha='left', va='center', zorder=8)

    # FC-37 Rain Sensor
    rn_x, rn_y, rn_w, rn_h = 3.35, 1.95, 3.10, 1.65
    rn_box = patches.Rectangle((rn_x, rn_y), rn_w, rn_h, facecolor='#ffffff', edgecolor='#000000', lw=1.8, zorder=4)
    ax.add_patch(rn_box)
    ax.text(rn_x + rn_w/2, rn_y + rn_h/2 + 0.22, "FC-37", fontsize=13.0, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(rn_x + rn_w/2, rn_y + rn_h/2 - 0.24, "(Cảm biến mưa bề mặt hồ)", fontsize=9.0, style='italic', ha='center', va='center', zorder=8)

    # FC-37 GND -> straight down to GND rail at x = 4.50
    draw_wire(ax, [(4.50, rn_y), (4.50, y_gnd)])
    draw_dot(ax, 4.50, y_gnd, r=0.08)
    ax.text(4.50, rn_y + 0.18, "GND", fontsize=10.0, fontweight='bold', ha='center', va='bottom', zorder=8)

    # ==========================================================
    # FUNCTIONAL GROUP 3: KHỐI XỬ LÝ TRUNG TÂM (ESP32 DevKit V1)
    # Placed at x = [10.60, 14.60], y = [1.70, 10.10]
    # ==========================================================
    esp_x, esp_y, esp_w, esp_h = 10.60, 1.70, 4.00, 8.40
    esp_box = patches.Rectangle((esp_x, esp_y), esp_w, esp_h, facecolor='#ffffff', edgecolor='#000000', lw=2.2, zorder=4)
    ax.add_patch(esp_box)

    # Header badge at top of ESP32 (neat, concise, centered at x = 12.35)
    ax.text(esp_x + 1.75, esp_y + esp_h,
            "KHỐI XỬ LÝ TRUNG TÂM\n(ESP32 DevKit V1)",
            fontsize=9.2, fontweight='bold', ha='center', va='center',
            bbox=dict(boxstyle="square,pad=0.25", facecolor='#ffffff', edgecolor='#000000', lw=1.3), zorder=9)

    # ESP32 Header inside box
    ax.text(esp_x + 1.75, esp_y + esp_h - 0.55, "ESP32 DevKit V1", fontsize=13.0, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(esp_x + 1.75, esp_y + esp_h - 0.88, "Vi Điều Khiển Trung Tâm (3.3V Logic)", fontsize=9.0, style='italic', ha='center', va='center', color='#333333', zorder=8)

    # Power connections on ESP32 (Placed at x = 14.30)
    # VIN (5V) -> +5V rail at x = 14.30
    draw_wire(ax, [(14.30, esp_y + esp_h), (14.30, y_5v)])
    draw_dot(ax, 14.30, y_5v, r=0.08)
    ax.text(14.30, esp_y + esp_h - 0.22, "VIN (5V)", fontsize=9.5, fontweight='bold', ha='center', va='top', zorder=8)

    # GND -> GND rail at x = 14.30
    draw_wire(ax, [(14.30, esp_y), (14.30, y_gnd)])
    draw_dot(ax, 14.30, y_gnd, r=0.08)
    ax.text(14.30, esp_y + 0.22, "GND", fontsize=9.5, fontweight='bold', ha='center', va='bottom', zorder=8)

    # ==========================================================
    # INTERACTION CHANNELS BETWEEN PC AND ESP32 (MONOCHROME B&W!)
    # Midpoint x = (6.70 + 10.60)/2 = 8.65
    # ==========================================================
    # Channel 1: Wi-Fi SoftAP at y = 8.75
    y_wifi = 8.75
    ant_box = patches.Rectangle((esp_x + 0.10, y_wifi - 0.32), 1.30, 0.64, facecolor='#ffffff', edgecolor='#000000', lw=1.5, zorder=6)
    ax.add_patch(ant_box)
    ax.text(esp_x + 0.75, y_wifi, "Wi-Fi (PCB)", fontsize=8.8, fontweight='bold', ha='center', va='center', zorder=8)

    # Horizontal Wireless Link (Dashed line with double arrow)
    draw_wire(ax, [(pc_x + pc_w, y_wifi), (esp_x, y_wifi)], lw=2.2, ls='--')
    ax.annotate("", xy=(esp_x - 0.05, y_wifi), xytext=(pc_x + pc_w + 0.05, y_wifi),
                arrowprops=dict(arrowstyle="<->", lw=2.2, color='#000000', linestyle='--'), zorder=9)
    # B&W Badge for Wi-Fi Channel
    ax.text(8.65, y_wifi,
            "SÓNG WI-FI 2.4 GHz (SoftAP: 192.168.4.1)\nWeb Dashboard & REST API Telemetry",
            fontsize=8.2, fontweight='bold', ha='center', va='center', color='#000000',
            bbox=dict(boxstyle="square,pad=0.25", facecolor="#ffffff", edgecolor="#000000", lw=1.2), zorder=11)

    # Channel 2: Micro-USB Port & USB-UART Bridge at y = 7.35
    y_usb = 7.35
    usb_box = patches.Rectangle((esp_x + 0.10, y_usb - 0.35), 1.45, 0.70, facecolor='#ffffff', edgecolor='#000000', lw=1.5, zorder=6)
    ax.add_patch(usb_box)
    ax.text(esp_x + 0.82, y_usb, "Micro-USB\n(CP2102 UART)", fontsize=8.2, fontweight='bold', ha='center', va='center', zorder=8)

    # Horizontal Wired Link (Solid line with B&W USB badge)
    draw_wire(ax, [(pc_x + pc_w, y_usb), (esp_x, y_usb)], lw=2.4, ls='-')
    ax.annotate("", xy=(esp_x - 0.05, y_usb), xytext=(pc_x + pc_w + 0.05, y_usb),
                arrowprops=dict(arrowstyle="<->", lw=2.4, color='#000000'), zorder=9)
    ax.text(8.65, y_usb,
            "CÁP USB (CP2102 UART 115200 bps)\nNạp Firmware PlatformIO & Serial Monitor",
            fontsize=8.2, fontweight='bold', ha='center', va='center', color='#000000',
            bbox=dict(boxstyle="square,pad=0.25", facecolor="#ffffff", edgecolor="#000000", lw=1.2), zorder=11)

    # ==========================================================
    # SENSOR CONNECTIONS TO ESP32 PINS
    # ==========================================================
    # D13 (TRIG) at y = 5.25
    y_trig = 5.25
    ax.text(esp_x + 0.15, y_trig, "D13 (TRIG)", fontsize=11.0, fontweight='bold', ha='left', va='center', zorder=8)
    ax.text(hc_x + hc_w - 0.14, y_trig, "TRIG", fontsize=10.5, fontweight='bold', ha='right', va='center', zorder=8)
    draw_wire(ax, [(hc_x + hc_w, y_trig), (esp_x, y_trig)])

    # D12 (ECHO) with Divider R1 (1k) + R2 (2k) -> GND at y = 4.35
    y_echo = 4.35
    ax.text(esp_x + 0.15, y_echo, "D12 (ECHO)", fontsize=11.0, fontweight='bold', ha='left', va='center', zorder=8)
    ax.text(hc_x + hc_w - 0.14, y_echo, "ECHO", fontsize=10.5, fontweight='bold', ha='right', va='center', zorder=8)
    draw_wire(ax, [(hc_x + hc_w, y_echo), (esp_x, y_echo)])
    draw_resistor_h(ax, 7.50, y_echo, label="R1", val="1kΩ", w=0.62, h=0.25, font_size=9.8)
    node_echo_x = 8.85
    draw_dot(ax, node_echo_x, y_echo, r=0.08)
    draw_wire(ax, [(node_echo_x, y_echo), (node_echo_x, y_gnd)])
    # Resistor R2 centered at y = 3.85 (height 0.55, spans 3.57 to 4.12, well ABOVE y = 3.25!)
    draw_resistor_v(ax, node_echo_x, 3.85, label="R2", val="2kΩ", h=0.55, w=0.24, label_side='left', font_size=9.5)
    draw_dot(ax, node_echo_x, y_gnd, r=0.08)

    # 3V3 Output to FC-37 VCC at y = 3.25
    y_3v3 = 3.25
    ax.text(esp_x + 0.15, y_3v3, "3V3 (OUT)", fontsize=11.0, fontweight='bold', ha='left', va='center', zorder=8)
    draw_wire(ax, [(esp_x, y_3v3), (rn_x + rn_w, y_3v3)])
    ax.text(rn_x + rn_w - 0.14, y_3v3, "VCC", fontsize=10.5, fontweight='bold', ha='right', va='center', zorder=8)

    # D34 (DO) at y = 2.65
    y_do = 2.65
    ax.text(esp_x + 0.15, y_do, "D34 (DO)", fontsize=11.0, fontweight='bold', ha='left', va='center', zorder=8)
    ax.text(rn_x + rn_w - 0.14, y_do, "DO", fontsize=10.5, fontweight='bold', ha='right', va='center', zorder=8)
    draw_wire(ax, [(rn_x + rn_w, y_do), (esp_x, y_do)])

    # D35 (AO) at y = 2.05
    y_ao = 2.05
    ax.text(esp_x + 0.15, y_ao, "D35 (AO)", fontsize=11.0, fontweight='bold', ha='left', va='center', zorder=8)
    ax.text(rn_x + rn_w - 0.14, y_ao, "AO", fontsize=10.5, fontweight='bold', ha='right', va='center', zorder=8)
    draw_wire(ax, [(rn_x + rn_w, y_ao), (esp_x, y_ao)])

    # ==========================================================
    # RIGHT SIDE OF ESP32: CONTROL PINS
    # ==========================================================
    right_pins_info = [
        ("D23 (RELAY)", 8.20),  # Relay K1
        ("D27 (PWM)",   7.00),  # Servo SG90
        ("D4 (BUZZ)",   5.80),  # Active Buzzer
        ("D18 (LED-R)", 5.00),  # LED Red
        ("D19 (LED-Y)", 4.20),  # LED Yellow
        ("D21 (LED-G)", 3.40),  # LED Green
    ]
    for pname, py in right_pins_info:
        ax.text(esp_x + esp_w - 0.15, py, pname, fontsize=11.0, fontweight='bold', ha='right', va='center', zorder=8)

    # ==========================================================
    # FUNCTIONAL GROUP 4: KHỐI CẢNH BÁO TẠI CHỖ (3 ĐÈN LED & CÒI BUZZER)
    # Placed at x = [15.00, 19.30], y = [1.55, 6.30] (width 4.30, height 4.75)
    # ==========================================================
    sig_x, sig_y, sig_w, sig_h = 15.00, 1.55, 4.30, 4.75
    draw_group_box(ax, sig_x, sig_y, sig_w, sig_h,
                   label="KHỐI CẢNH BÁO TẠI CHỖ\n(3 ĐÈN LED CHỈ THỊ & CÒI BUZZER)",
                   badge_y=sig_y + sig_h, badge_fs=9.0)

    # All 3 LED Resistors centered in a clean row at yc = 2.85
    # All 3 LEDs centered in a clean row at yc = 2.05
    # D21 (Green, x=15.50, pin y=3.40):
    bx_g = 15.50
    draw_wire(ax, [(esp_x + esp_w, 3.40), (bx_g, 3.40), (bx_g, y_gnd)])
    draw_dot(ax, bx_g, y_gnd, r=0.08)
    draw_resistor_v(ax, bx_g, 2.85, label="R3", val="220Ω", h=0.52, w=0.24, label_side='left', font_size=8.8)
    draw_led_v(ax, bx_g, 2.05, label="H1\n(Xanh)", font_size=8.6)

    # D19 (Yellow, x=16.50, pin y=4.20):
    bx_y = 16.50
    draw_wire(ax, [(esp_x + esp_w, 4.20), (bx_y, 4.20), (bx_y, y_gnd)])
    draw_dot(ax, bx_y, y_gnd, r=0.08)
    draw_resistor_v(ax, bx_y, 2.85, label="R4", val="220Ω", h=0.52, w=0.24, label_side='left', font_size=8.8)
    draw_led_v(ax, bx_y, 2.05, label="H2\n(Vàng)", font_size=8.6)

    # D18 (Red, x=17.50, pin y=5.00):
    bx_r = 17.50
    draw_wire(ax, [(esp_x + esp_w, 5.00), (bx_r, 5.00), (bx_r, y_gnd)])
    draw_dot(ax, bx_r, y_gnd, r=0.08)
    draw_resistor_v(ax, bx_r, 2.85, label="R5", val="220Ω", h=0.52, w=0.24, label_side='left', font_size=8.8)
    draw_led_v(ax, bx_r, 2.05, label="H3\n(Đỏ)", font_size=8.6)

    # Branch 4: Active Buzzer 5V (D4, y=5.80, x=18.60)
    py_bz, bx_bz = 5.80, 18.60
    draw_wire(ax, [(esp_x + esp_w, py_bz), (bx_bz, py_bz), (bx_bz, y_gnd)])
    draw_dot(ax, bx_bz, y_gnd, r=0.08)
    draw_resistor_v(ax, bx_bz, 4.45, label="R6", val="100Ω", h=0.54, w=0.24, label_side='left', font_size=8.8)
    bz_r = 0.35
    bz_y = 2.80
    bz_circle = plt.Circle((bx_bz, bz_y), bz_r, facecolor='#ffffff', edgecolor='#000000', lw=2.0, zorder=7)
    ax.add_patch(bz_circle)
    ax.text(bx_bz, bz_y, "BZ", fontsize=11.5, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(bx_bz + 0.44, bz_y, "Còi\n5V", fontsize=9.8, fontweight='bold', ha='left', va='center', zorder=10)

    # ==========================================================
    # FUNCTIONAL GROUP 5: KHỐI CHẤP HÀNH 1 - CỬA VAN XẢ LŨ (SERVO SG90 & C1)
    # Placed at x = [19.60, 21.95], y = [1.55, 10.10] (width 2.35)
    # ==========================================================
    sv_grp_x, sv_grp_y, sv_grp_w, sv_grp_h = 19.60, 1.55, 2.35, 8.55
    draw_group_box(ax, sv_grp_x, sv_grp_y, sv_grp_w, sv_grp_h,
                   label="KHỐI CHẤP HÀNH 1\nCỬA VAN XẢ (SERVO SG90)",
                   badge_y=sv_grp_y + sv_grp_h, badge_fs=8.8)

    py_sv, bx_sv = 7.00, 20.25
    sv_w, sv_h = 1.05, 1.30
    sv_box = patches.Rectangle((bx_sv - sv_w/2, py_sv - sv_h/2), sv_w, sv_h,
                               facecolor='#ffffff', edgecolor='#000000', lw=2.0, zorder=6)
    ax.add_patch(sv_box)
    ax.text(bx_sv, py_sv + 0.20, "SG90", fontsize=12.0, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(bx_sv, py_sv - 0.24, "Servo\nVan Xả", fontsize=9.5, fontweight='bold', ha='center', va='center', zorder=8)

    # Signal D27 -> Servo (wire runs cleanly above Group 4 at y=7.00 > 6.30!)
    draw_wire(ax, [(esp_x + esp_w, py_sv), (bx_sv - sv_w/2, py_sv)])

    # +5V -> Servo top, Servo bottom -> GND
    draw_wire(ax, [(bx_sv, y_5v), (bx_sv, py_sv + sv_h/2)])
    draw_dot(ax, bx_sv, y_5v, r=0.08)
    draw_wire(ax, [(bx_sv, py_sv - sv_h/2), (bx_sv, y_gnd)])
    draw_dot(ax, bx_sv, y_gnd, r=0.08)

    # Filter Capacitor C1 (220uF) at x=21.35
    cx = 21.35
    draw_wire(ax, [(cx, y_5v), (cx, y_gnd)])
    draw_dot(ax, cx, y_5v, r=0.08)
    draw_dot(ax, cx, y_gnd, r=0.08)
    draw_capacitor_v(ax, cx, 4.50, label="C1\n220µF", font_size=10.5)

    # ==========================================================
    # FUNCTIONAL GROUP 6: KHỐI CHẤP HÀNH 2 - MÁY BƠM (RELAY 5V & MOTOR)
    # Placed at x = [22.25, 24.85], y = [1.55, 10.10] (width 2.60)
    # Encloses Relay Coil K1, Diode D1, NO Contact K1, Fuse F2, Motor M
    # ZERO CROSSINGS: D23 drops on LEFT, linkage goes RIGHT to contact!
    # ==========================================================
    pump_grp_x, pump_grp_y, pump_grp_w, pump_grp_h = 22.25, 1.55, 2.60, 8.55
    draw_group_box(ax, pump_grp_x, pump_grp_y, pump_grp_w, pump_grp_h,
                   label="KHỐI CHẤP HÀNH 2\nMÁY BƠM (RELAY 5V)",
                   badge_y=pump_grp_y + pump_grp_h, badge_fs=8.8)

    x_d23_drop = 22.45
    x_diode    = 22.75
    x_coil     = 23.20
    x_motor_br = 24.25

    coil_w, coil_h = 0.65, 1.00
    coil_yc = 6.60
    # Lead wire extension above and below coil box for clean terminal junctions
    y_lead_top = coil_yc + coil_h/2 + 0.20  # 7.30
    y_lead_bot = coil_yc - coil_h/2 - 0.20  # 5.90

    # +5V to top lead terminal of coil K1
    draw_wire(ax, [(x_coil, y_5v), (x_coil, coil_yc + coil_h/2)])
    draw_dot(ax, x_coil, y_5v, r=0.08)
    draw_dot(ax, x_coil, y_lead_top, r=0.08)

    # Coil K1 Rectangle
    coil_rect = patches.Rectangle((x_coil - coil_w/2, coil_yc - coil_h/2), coil_w, coil_h,
                                  facecolor='#ffffff', edgecolor='#000000', lw=2.0, zorder=6)
    ax.add_patch(coil_rect)
    ax.text(x_coil, coil_yc + 0.16, "K1", fontsize=12.0, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(x_coil, coil_yc - 0.20, "(5V)", fontsize=9.5, fontweight='bold', ha='center', va='center', zorder=8)

    # Flyback Diode D1 across Relay Coil K1 (cathode at y_lead_top, anode at y_lead_bot)
    draw_wire(ax, [(x_coil, y_lead_top), (x_diode, y_lead_top), (x_diode, y_lead_bot), (x_coil, y_lead_bot)])
    draw_dot(ax, x_coil, y_lead_bot, r=0.08)
    draw_diode_up(ax, x_diode, coil_yc, label="D1", font_size=10.0)

    # D23 (Active LOW) route:
    # Comes from ESP32 at y = 8.20, turns down at x = 22.45,
    # drops to y = 5.30 (below coil), turns right to x = 23.20, goes up to bottom terminal!
    py_rl = 8.20
    draw_wire(ax, [(esp_x + esp_w, py_rl), (x_d23_drop, py_rl), (x_d23_drop, 5.30), (x_coil, 5.30), (x_coil, coil_yc - coil_h/2)])

    # Sub-circuit B: Pump Motor Power Branch (x = 24.25)
    draw_wire(ax, [(x_motor_br, y_5v), (x_motor_br, y_gnd)])
    draw_dot(ax, x_motor_br, y_5v, r=0.08)
    draw_dot(ax, x_motor_br, y_gnd, r=0.08)

    draw_fuse_v(ax, x_motor_br, 8.85, label="F2\n(1.5A)", h=0.60, w=0.24, font_size=10.0)
    draw_switch_no_v(ax, x_motor_br, coil_yc, label="K1", h=0.65, font_size=12.0)

    # Dashed mechanical linkage from K1 coil right edge to K1 NO contact (COMPLETELY UNOBSTRUCTED!)
    draw_wire(ax, [(x_coil + coil_w/2, coil_yc), (x_motor_br - 0.18, coil_yc)], lw=1.6, ls='--')

    # Motor M symbol
    m_r = 0.46
    m_yc = 3.60
    m_circle = plt.Circle((x_motor_br, m_yc), m_r, facecolor='#ffffff', edgecolor='#000000', lw=2.2, zorder=7)
    ax.add_patch(m_circle)
    ax.text(x_motor_br, m_yc, "M", fontsize=16.0, fontweight='bold', ha='center', va='center', zorder=8)
    # Motor Label with white background mask to cleanly avoid wire intersection!
    ax.text(x_motor_br, m_yc - m_r - 0.28, "Bơm Mini 5V", fontsize=10.0, fontweight='bold', ha='center', va='top',
            bbox=dict(boxstyle="square,pad=0.12", facecolor='#ffffff', edgecolor='none'), zorder=10)

    # ==========================================================
    # LEGEND BAR AT BOTTOM (Clean & perfectly centered within borders)
    # ==========================================================
    ax.plot([0.50, 25.00], [1.05, 1.05], color='#000000', lw=1.0)
    legend_line1 = (
        "CHÚ THÍCH KÝ HIỆU TIÊU CHUẨN IEC:   "
        "[PC] Máy tính vận hành (Web Dashboard & PlatformIO)   |   "
        "[S1] Công tắc nguồn chính   |   "
        "[F1, F2] Cầu chì quá dòng   |   "
        "[R1, R2] Cầu phân áp Echo (5V → 3.3V)"
    )
    legend_line2 = (
        "[R3–R6] Điện trở hạn dòng LED & Còi   |   "
        "[H1–H3] Đèn LED chỉ thị 3 cấp   |   "
        "[BZ] Còi báo Active Buzzer 5V   |   "
        "[C1] Tụ lọc nguồn Servo   |   "
        "[K1] Rơ-le điều khiển bơm (Active LOW)   |   "
        "[D1] Diode dập xung ngược   |   "
        "[M] Bơm mini 5V"
    )
    ax.text(12.75, 0.80, legend_line1, fontsize=9.4, ha='center', va='center', zorder=10)
    ax.text(12.75, 0.54, legend_line2, fontsize=9.4, ha='center', va='center', zorder=10)

    for p in out_paths:
        fig.savefig(p, dpi=300, bbox_inches='tight', facecolor='#ffffff')
        print(f"Saved circuit diagram to: {p}")
    plt.close(fig)


if __name__ == "__main__":
    create_circuit_diagram()
