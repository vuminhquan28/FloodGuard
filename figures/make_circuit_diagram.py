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
plt.rcParams['text.color'] = '#000000'


def draw_dot(ax, x, y, r=0.055):
    dot = plt.Circle((x, y), r, facecolor='#000000', edgecolor='#000000', zorder=12)
    ax.add_patch(dot)


def draw_wire(ax, pts, lw=1.5, ls='-', zorder=3):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs, ys, color='#000000', lw=lw, linestyle=ls, zorder=zorder,
            solid_capstyle='butt', solid_joinstyle='miter')


def draw_resistor_v(ax, x, yc, label="", val="", h=0.60, w=0.22, label_side='right'):
    """IEC standard rectangular resistor vertical"""
    rect = patches.Rectangle((x - w/2, yc - h/2), w, h, facecolor='#ffffff',
                             edgecolor='#000000', lw=1.4, zorder=7)
    ax.add_patch(rect)
    if label or val:
        txt = f"{label}\n{val}".strip()
        if label_side == 'left':
            ax.text(x - w/2 - 0.08, yc, txt, fontsize=7.5, ha='right', va='center', zorder=10)
        else:
            ax.text(x + w/2 + 0.08, yc, txt, fontsize=7.5, ha='left', va='center', zorder=10)


def draw_resistor_h(ax, xc, y, label="", val="", w=0.60, h=0.22):
    """IEC standard rectangular resistor horizontal"""
    rect = patches.Rectangle((xc - w/2, y - h/2), w, h, facecolor='#ffffff',
                             edgecolor='#000000', lw=1.4, zorder=7)
    ax.add_patch(rect)
    if label or val:
        txt = f"{label} ({val})".strip()
        ax.text(xc, y + h/2 + 0.08, txt, fontsize=7.5, ha='center', va='bottom', zorder=10)


def draw_fuse_h(ax, xc, y, label="F1 (2A)", w=0.52, h=0.18):
    """IEC fuse symbol horizontal"""
    rect = patches.Rectangle((xc - w/2, y - h/2), w, h, facecolor='#ffffff',
                             edgecolor='#000000', lw=1.4, zorder=7)
    ax.add_patch(rect)
    ax.plot([xc - w/2 - 0.08, xc + w/2 + 0.08], [y, y], color='#000000', lw=1.4, zorder=8)
    ax.text(xc, y + h/2 + 0.10, label, fontsize=8.0, fontweight='bold', ha='center', va='bottom', zorder=10)


def draw_fuse_v(ax, x, yc, label="F2", h=0.52, w=0.18):
    """IEC fuse symbol vertical"""
    rect = patches.Rectangle((x - w/2, yc - h/2), w, h, facecolor='#ffffff',
                             edgecolor='#000000', lw=1.4, zorder=7)
    ax.add_patch(rect)
    ax.plot([x, x], [yc - h/2 - 0.08, yc + h/2 + 0.08], color='#000000', lw=1.4, zorder=8)
    ax.text(x + w/2 + 0.10, yc, label, fontsize=8.0, fontweight='bold', ha='left', va='center', zorder=10)


def draw_led_v(ax, x, yc, label=""):
    """IEC LED symbol pointing down"""
    w = 0.28
    h = 0.26
    # White mask behind LED so vertical wire does not show inside triangle
    mask = patches.Rectangle((x - w/2 - 0.02, yc - h/2 - 0.02), w + 0.04, h + 0.04,
                             facecolor='#ffffff', edgecolor='none', zorder=6)
    ax.add_patch(mask)
    tri = patches.Polygon([[x - w/2, yc + h/2], [x + w/2, yc + h/2], [x, yc - h/2]],
                          closed=True, facecolor='#ffffff', edgecolor='#000000', lw=1.4, zorder=7)
    ax.add_patch(tri)
    ax.plot([x - w/2, x + w/2], [yc - h/2, yc - h/2], color='#000000', lw=1.6, zorder=8)
    # Emission arrows
    ax.annotate("", xy=(x + 0.36, yc - 0.02), xytext=(x + 0.16, yc + 0.14),
                arrowprops=dict(arrowstyle="->", lw=1.0, color='#000000'), zorder=9)
    ax.annotate("", xy=(x + 0.36, yc - 0.16), xytext=(x + 0.16, yc),
                arrowprops=dict(arrowstyle="->", lw=1.0, color='#000000'), zorder=9)
    if label:
        ax.text(x + 0.38, yc + 0.02, label, fontsize=7.5, fontweight='bold', ha='left', va='center', zorder=10)


def draw_diode_up(ax, x, yc, label="D1"):
    """Flyback diode pointing up"""
    w = 0.22
    h = 0.22
    mask = patches.Rectangle((x - w/2 - 0.02, yc - h/2 - 0.02), w + 0.04, h + 0.04,
                             facecolor='#ffffff', edgecolor='none', zorder=6)
    ax.add_patch(mask)
    tri = patches.Polygon([[x - w/2, yc - h/2], [x + w/2, yc - h/2], [x, yc + h/2]],
                          closed=True, facecolor='#ffffff', edgecolor='#000000', lw=1.4, zorder=7)
    ax.add_patch(tri)
    ax.plot([x - w/2, x + w/2], [yc + h/2, yc + h/2], color='#000000', lw=1.5, zorder=8)
    if label:
        ax.text(x - w/2 - 0.05, yc, label, fontsize=7.2, fontweight='bold', ha='right', va='center', zorder=10)


def draw_capacitor_v(ax, x, yc, label="C1\n220µF"):
    """Polarized capacitor vertical with clean gap mask"""
    w = 0.34
    gap = 0.12
    mask = patches.Rectangle((x - w/2, yc - gap/2), w, gap, facecolor='#ffffff', edgecolor='none', zorder=6)
    ax.add_patch(mask)
    ax.plot([x - w/2, x + w/2], [yc + gap/2, yc + gap/2], color='#000000', lw=1.8, zorder=8)
    ax.plot([x - w/2, x + w/2], [yc - gap/2, yc - gap/2], color='#000000', lw=1.8, zorder=8)
    ax.text(x - w/2 - 0.04, yc + 0.14, "+", fontsize=8.5, fontweight='bold', ha='right', va='center', zorder=10)
    ax.text(x + w/2 + 0.06, yc, label, fontsize=7.2, ha='left', va='center', zorder=10)


def draw_switch_no_v(ax, x, yc, label="K1", h=0.46):
    """Normally Open (NO) contact vertical in IEC style"""
    mask = patches.Rectangle((x - 0.28, yc - h/2), 0.56, h, facecolor='#ffffff', edgecolor='none', zorder=6)
    ax.add_patch(mask)
    ax.plot([x, x - 0.22], [yc - h/2, yc + h/2 - 0.04], color='#000000', lw=1.7, zorder=8)
    draw_dot(ax, x, yc - h/2, r=0.045)
    draw_dot(ax, x, yc + h/2, r=0.045)
    ax.text(x + 0.15, yc, label, fontsize=8.5, fontweight='bold', ha='left', va='center', zorder=10)


def draw_switch_no_h(ax, xc, y, label="S1", w=0.46):
    """Normally Open (NO) switch horizontal"""
    mask = patches.Rectangle((xc - w/2, y - 0.25), w, 0.50, facecolor='#ffffff', edgecolor='none', zorder=6)
    ax.add_patch(mask)
    ax.plot([xc - w/2, xc + w/2 - 0.04], [y, y + 0.22], color='#000000', lw=1.7, zorder=8)
    draw_dot(ax, xc - w/2, y, r=0.045)
    draw_dot(ax, xc + w/2, y, r=0.045)
    ax.text(xc, y + 0.28, label, fontsize=8.0, fontweight='bold', ha='center', va='bottom', zorder=10)


def create_circuit_diagram():
    fig, ax = plt.subplots(figsize=(17.8, 9.6), dpi=300)
    ax.set_xlim(0, 17.8)
    ax.set_ylim(0, 9.6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Clean outer border
    border = patches.Rectangle((0.25, 0.25), 17.30, 9.1, facecolor='#ffffff', edgecolor='#000000', lw=1.3, zorder=1)
    ax.add_patch(border)

    # Header inside border
    ax.text(8.90, 9.02, "SƠ ĐỒ NGUYÊN LÝ MẠCH ĐIỆN HỆ THỐNG FLOODGUARD",
            fontsize=13.5, fontweight='bold', ha='center', va='center', zorder=10)
    ax.text(8.90, 8.72, "Chuẩn ký hiệu IEC đơn giản: Khối Cảm Biến  |  Vi điều khiển ESP32  |  Nhánh Cảnh Báo & Chấp Hành  |  Mạch Động Lực Bơm",
            fontsize=8.6, style='italic', ha='center', va='center', color='#333333', zorder=10)

    # ==========================================================
    # MAIN HORIZONTAL POWER & GROUND RAILS (like L and N in sample)
    # ==========================================================
    y_5v  = 7.95   # +5V rail
    y_gnd = 1.25   # Common GND rail

    # +5V Supply Entry (Top Left)
    ax.text(0.45, y_5v, "+5V DC\n(2A)", fontsize=8.5, fontweight='bold', ha='left', va='center', zorder=10)
    draw_wire(ax, [(1.20, y_5v), (16.45, y_5v)], lw=1.8)
    draw_dot(ax, 1.20, y_5v, r=0.06)

    # Main Switch S1 & Fuse F1 BEFORE all branches
    draw_switch_no_h(ax, 1.55, y_5v, label="S1", w=0.42)
    draw_fuse_h(ax, 2.25, y_5v, label="F1 (2A)", w=0.46, h=0.18)

    # Common GND Rail (Bottom)
    ax.text(0.45, y_gnd, "GND\n(Chung)", fontsize=8.5, fontweight='bold', ha='left', va='center', zorder=10)
    draw_wire(ax, [(1.20, y_gnd), (16.45, y_gnd)], lw=1.8)
    draw_dot(ax, 1.20, y_gnd, r=0.06)

    # ==========================================================
    # LEFT SIDE: SENSORS (HC-SR04 & FC-37)
    # ==========================================================
    # 1. HC-SR04 Ultrasonic Sensor
    hc_x, hc_y, hc_w, hc_h = 1.55, 4.70, 1.85, 1.85
    hc_box = patches.Rectangle((hc_x, hc_y), hc_w, hc_h, facecolor='#ffffff', edgecolor='#000000', lw=1.6, zorder=4)
    ax.add_patch(hc_box)
    ax.text(hc_x + hc_w/2, hc_y + hc_h/2 + 0.15, "HC-SR04", fontsize=9.8, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(hc_x + hc_w/2, hc_y + hc_h/2 - 0.18, "(Siêu âm)", fontsize=8.0, style='italic', ha='center', va='center', zorder=8)

    # HC-SR04 VCC -> +5V rail (AFTER fuse F1, at x=2.70)
    draw_wire(ax, [(2.70, hc_y + hc_h), (2.70, y_5v)])
    draw_dot(ax, 2.70, y_5v)
    ax.text(2.70, hc_y + hc_h - 0.10, "VCC", fontsize=7.2, fontweight='bold', ha='center', va='top', zorder=8)

    # HC-SR04 GND -> route cleanly to the LEFT (x=1.25) down to GND rail without crossing FC-37!
    draw_wire(ax, [(hc_x, hc_y + 0.30), (1.25, hc_y + 0.30), (1.25, y_gnd)])
    draw_dot(ax, 1.25, y_gnd)
    ax.text(hc_x + 0.10, hc_y + 0.30, "GND", fontsize=7.2, fontweight='bold', ha='left', va='center', zorder=8)

    # 2. Rain Sensor FC-37
    rn_x, rn_y, rn_w, rn_h = 1.55, 2.15, 1.85, 1.75
    rn_box = patches.Rectangle((rn_x, rn_y), rn_w, rn_h, facecolor='#ffffff', edgecolor='#000000', lw=1.6, zorder=4)
    ax.add_patch(rn_box)
    ax.text(rn_x + rn_w/2, rn_y + rn_h/2 + 0.15, "FC-37", fontsize=9.8, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(rn_x + rn_w/2, rn_y + rn_h/2 - 0.18, "(Cảm biến mưa)", fontsize=7.8, style='italic', ha='center', va='center', zorder=8)

    # FC-37 GND -> straight down to GND rail
    draw_wire(ax, [(2.47, rn_y), (2.47, y_gnd)])
    draw_dot(ax, 2.47, y_gnd)
    ax.text(2.47, rn_y + 0.10, "GND", fontsize=7.2, fontweight='bold', ha='center', va='bottom', zorder=8)

    # ==========================================================
    # CENTER: ESP32 DEVKIT V1
    # ==========================================================
    esp_x, esp_y, esp_w, esp_h = 5.10, 2.15, 3.20, 5.15
    esp_box = patches.Rectangle((esp_x, esp_y), esp_w, esp_h, facecolor='#ffffff', edgecolor='#000000', lw=2.0, zorder=4)
    ax.add_patch(esp_box)

    ax.text(esp_x + esp_w/2, esp_y + esp_h/2 + 0.30, "ESP32", fontsize=12.0, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(esp_x + esp_w/2, esp_y + esp_h/2 - 0.15, "DevKit V1\n(Logic 3.3V)", fontsize=8.4, ha='center', va='center', zorder=8)

    # ESP32 VIN (+5V)
    draw_wire(ax, [(6.70, esp_y + esp_h), (6.70, y_5v)])
    draw_dot(ax, 6.70, y_5v)
    ax.text(6.70, esp_y + esp_h - 0.12, "VIN (5V)", fontsize=7.6, fontweight='bold', ha='center', va='top', zorder=8)

    # ESP32 GND -> GND rail
    draw_wire(ax, [(6.70, esp_y), (6.70, y_gnd)])
    draw_dot(ax, 6.70, y_gnd)
    ax.text(6.70, esp_y + 0.12, "GND", fontsize=7.6, fontweight='bold', ha='center', va='bottom', zorder=8)

    # 3V3 Output to FC-37 VCC (cleanly routed between sensors)
    ax.text(esp_x + 0.12, 6.85, "3V3", fontsize=7.6, fontweight='bold', ha='left', va='center', zorder=8)
    draw_wire(ax, [(esp_x, 6.85), (3.75, 6.85), (3.75, 3.60), (rn_x + rn_w, 3.60)])
    ax.text(rn_x + rn_w - 0.08, 3.60, "VCC", fontsize=7.2, fontweight='bold', ha='right', va='center', zorder=8)

    # Left Pins of ESP32 & Wiring from Sensors
    # D13 (TRIG)
    y_trig = 6.00
    ax.text(esp_x + 0.12, y_trig, "D13 (TRIG)", fontsize=7.8, fontweight='bold', ha='left', va='center', zorder=8)
    ax.text(hc_x + hc_w - 0.08, y_trig, "TRIG", fontsize=7.2, fontweight='bold', ha='right', va='center', zorder=8)
    draw_wire(ax, [(hc_x + hc_w, y_trig), (esp_x, y_trig)])

    # D12 (ECHO) with Voltage Divider R1 (1k) + R2 (2k) -> GND
    y_echo = 5.15
    ax.text(esp_x + 0.12, y_echo, "D12 (ECHO)", fontsize=7.8, fontweight='bold', ha='left', va='center', zorder=8)
    ax.text(hc_x + hc_w - 0.08, y_echo, "ECHO", fontsize=7.2, fontweight='bold', ha='right', va='center', zorder=8)
    draw_wire(ax, [(hc_x + hc_w, y_echo), (esp_x, y_echo)])
    draw_resistor_h(ax, 4.12, y_echo, label="R1", val="1kΩ", w=0.52, h=0.20)
    node_echo_x = 4.72
    draw_dot(ax, node_echo_x, y_echo)
    draw_wire(ax, [(node_echo_x, y_echo), (node_echo_x, y_gnd)])
    draw_resistor_v(ax, node_echo_x, 3.95, label="R2", val="2kΩ", h=0.52, w=0.20, label_side='left')
    draw_dot(ax, node_echo_x, y_gnd)

    # D34 (DO)
    y_do = 3.05
    ax.text(esp_x + 0.12, y_do, "D34 (DO)", fontsize=7.8, fontweight='bold', ha='left', va='center', zorder=8)
    ax.text(rn_x + rn_w - 0.08, y_do, "DO", fontsize=7.2, fontweight='bold', ha='right', va='center', zorder=8)
    draw_wire(ax, [(rn_x + rn_w, y_do), (esp_x, y_do)])

    # D35 (AO)
    y_ao = 2.45
    ax.text(esp_x + 0.12, y_ao, "D35 (AO)", fontsize=7.8, fontweight='bold', ha='left', va='center', zorder=8)
    ax.text(rn_x + rn_w - 0.08, y_ao, "AO", fontsize=7.2, fontweight='bold', ha='right', va='center', zorder=8)
    draw_wire(ax, [(rn_x + rn_w, y_ao), (esp_x, y_ao)])

    # ==========================================================
    # RIGHT SIDE OF ESP32: PLANAR CONTROL BRANCHES (ZERO WIRE CROSSINGS!)
    # Ordered Top-to-Bottom from rightmost to leftmost branch
    # ==========================================================
    right_pins_info = [
        ("D23 (RELAY)", 6.55),  # Far right -> Relay K1
        ("D27 (PWM)",   5.75),  # Servo SG90
        ("D4 (BUZZ)",   4.95),  # Active Buzzer
        ("D18 (LED-R)", 4.20),  # LED Red
        ("D19 (LED-Y)", 3.55),  # LED Yellow
        ("D21 (LED-G)", 2.90),  # LED Green
    ]
    for pname, py in right_pins_info:
        ax.text(esp_x + esp_w - 0.12, py, pname, fontsize=7.6, fontweight='bold', ha='right', va='center', zorder=8)

    # Branches 1, 2, 3: LEDs (Left-to-Right: LED-G, LED-Y, LED-R)
    led_configs = [
        (2.90, 9.00,  "R3", "220Ω", "H1\n(Xanh)"),
        (3.55, 10.15, "R4", "220Ω", "H2\n(Vàng)"),
        (4.20, 11.30, "R5", "220Ω", "H3\n(Đỏ)"),
    ]
    for py, bx, r_lbl, r_val, l_lbl in led_configs:
        draw_wire(ax, [(esp_x + esp_w, py), (bx, py), (bx, y_gnd)])
        draw_dot(ax, bx, y_gnd)
        draw_resistor_v(ax, bx, 2.45, label=r_lbl, val=r_val, h=0.48, w=0.20)
        draw_led_v(ax, bx, 1.72, label=l_lbl)

    # Branch 4: Active Buzzer 5V (D4, y=4.95, x=12.45)
    py_bz, bx_bz = 4.95, 12.45
    draw_wire(ax, [(esp_x + esp_w, py_bz), (bx_bz, py_bz), (bx_bz, y_gnd)])
    draw_dot(ax, bx_bz, y_gnd)
    draw_resistor_v(ax, bx_bz, 3.60, label="R6", val="100Ω", h=0.52, w=0.20)
    bz_r = 0.25
    bz_circle = plt.Circle((bx_bz, 2.25), bz_r, facecolor='#ffffff', edgecolor='#000000', lw=1.6, zorder=7)
    ax.add_patch(bz_circle)
    ax.text(bx_bz, 2.25, "BZ", fontsize=8.0, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(bx_bz + 0.32, 2.25, "Còi\n5V", fontsize=7.5, fontweight='bold', ha='left', va='center', zorder=10)

    # Branch 5: Servo SG90 (D27, y=5.75, x=13.55) + Parallel Filter C1 (x=14.15)
    py_sv, bx_sv = 5.75, 13.55
    sv_w, sv_h = 0.85, 1.00
    sv_box = patches.Rectangle((bx_sv - sv_w/2, py_sv - sv_h/2), sv_w, sv_h,
                               facecolor='#ffffff', edgecolor='#000000', lw=1.6, zorder=6)
    ax.add_patch(sv_box)
    ax.text(bx_sv, py_sv + 0.14, "SG90", fontsize=8.8, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(bx_sv, py_sv - 0.18, "Servo\nVan xả", fontsize=7.0, ha='center', va='center', zorder=8)
    # Signal D27 -> Servo
    draw_wire(ax, [(esp_x + esp_w, py_sv), (bx_sv - sv_w/2, py_sv)])
    # +5V -> Servo top, Servo bottom -> GND
    draw_wire(ax, [(bx_sv, y_5v), (bx_sv, py_sv + sv_h/2)])
    draw_dot(ax, bx_sv, y_5v)
    draw_wire(ax, [(bx_sv, py_sv - sv_h/2), (bx_sv, y_gnd)])
    draw_dot(ax, bx_sv, y_gnd)

    # Filter Capacitor C1 (220uF) across +5V and GND at x=14.18 (below D23 line? No, D23 is at 6.55; put C1 from +5V down to GND at x=14.15? Wait: D23 goes horizontally at y=6.55 to x=15.05, so C1 at x=14.18 would cross D23 cleanly, or place C1 on the LEFT of Servo or BELOW D23? No, C1 goes to +5V (y=7.95)! Putting C1 at x=14.18 with clean bridge or putting C1 at x=13.55? Actually, put C1 between +5V and GND at x=14.18 is fine if D23 goes at y=6.55 and C1 plate is at y=4.00 — just crossing one wire cleanly, OR put D23 above +5V? No! Put Servo + C1 at x=13.45 and C1 leg connecting to Servo's +5V/GND leg!)
    # Even cleaner: branch off Servo's vertical +5V line at y=7.30 -> x=14.10 -> down to y=2.00 -> back to Servo's GND line! That way it NEVER crosses D23!
    # Wait: D23 is at y=6.55, so branching from Servo at y=7.30 down to y=2.00 STILL passes y=6.55!
    # Wait: if Servo is at x=13.55, Relay is at x=15.10, and C1 is on the LEFT side of Servo at x=13.00? Still crosses D27!
    # What if Servo & C1 are to the RIGHT of Relay? No, Relay needs to be closest to Pump Power Circuit for the dashed mechanical link K1!
    # Wait: Crossing D23 horizontally at y=6.55 with one vertical wire of C1 is totally normal in schematics as long as there's no dot (and no component overlap). Or even better: make D23 wire route at y=6.55 and C1 capacitor symbol at y=3.60 (well away from y=6.55)! Let's do that!
    cx = 13.95
    draw_wire(ax, [(cx, y_5v), (cx, y_gnd)])
    draw_dot(ax, cx, y_5v)
    draw_dot(ax, cx, y_gnd)
    draw_capacitor_v(ax, cx, 3.60, label="C1\n220µF")

    # Branch 6: Relay Coil K1 (D23, y=6.55, x=15.25)
    py_rl, bx_rl = 6.55, 15.25
    coil_w, coil_h = 0.54, 0.86
    coil_y = 5.00
    draw_wire(ax, [(bx_rl, y_5v), (bx_rl, coil_y + coil_h/2)])
    draw_dot(ax, bx_rl, y_5v)
    draw_wire(ax, [(esp_x + esp_w, py_rl), (14.32, py_rl), (14.32, coil_y - 0.80), (bx_rl, coil_y - 0.80), (bx_rl, coil_y - coil_h/2)])

    coil_rect = patches.Rectangle((bx_rl - coil_w/2, coil_y - coil_h/2), coil_w, coil_h,
                                  facecolor='#ffffff', edgecolor='#000000', lw=1.7, zorder=6)
    ax.add_patch(coil_rect)
    ax.text(bx_rl, coil_y + 0.12, "K1", fontsize=9.5, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(bx_rl, coil_y - 0.16, "(5V)", fontsize=7.5, fontweight='bold', ha='center', va='center', zorder=8)

    # Flyback Diode D1 across Relay Coil K1 (on the left of coil at x = 14.77)
    dx_fb = bx_rl - 0.48
    draw_wire(ax, [(bx_rl, coil_y + 0.58), (dx_fb, coil_y + 0.58), (dx_fb, coil_y - 0.58), (bx_rl, coil_y - 0.58)])
    draw_dot(ax, bx_rl, coil_y + 0.58)
    draw_dot(ax, bx_rl, coil_y - 0.58)
    draw_diode_up(ax, dx_fb, coil_y, label="D1")

    # ==========================================================
    # FAR RIGHT: PUMP POWER CIRCUIT (MẠCH ĐỘNG LỰC MÁY BƠM)
    # ==========================================================
    draw_wire(ax, [(15.80, 8.20), (15.80, 1.00)], lw=1.0, ls=':')
    ax.text(8.3, 8.25, "MẠCH ĐIỀU KHIỂN & CẢM BIẾN (CONTROL)", fontsize=8.5, fontweight='bold', ha='center', va='bottom', zorder=10)
    ax.text(16.45, 8.25, "MẠCH ĐỘNG LỰC", fontsize=8.5, fontweight='bold', ha='center', va='bottom', zorder=10)

    px_pump = 16.45
    draw_wire(ax, [(px_pump, y_5v), (px_pump, y_gnd)])
    draw_dot(ax, px_pump, y_5v)
    draw_dot(ax, px_pump, y_gnd)

    draw_fuse_v(ax, px_pump, 6.70, label="F2", h=0.45, w=0.18)
    draw_switch_no_v(ax, px_pump, coil_y, label="K1", h=0.50)

    # Dashed mechanical linkage from K1 coil to K1 NO contact
    draw_wire(ax, [(bx_rl + coil_w/2, coil_y), (px_pump - 0.14, coil_y)], lw=1.3, ls='--')

    # Motor M symbol
    m_r = 0.40
    m_y = 2.65
    m_circle = plt.Circle((px_pump, m_y), m_r, facecolor='#ffffff', edgecolor='#000000', lw=1.8, zorder=7)
    ax.add_patch(m_circle)
    ax.text(px_pump, m_y, "M", fontsize=12.0, fontweight='bold', ha='center', va='center', zorder=8)
    ax.text(px_pump + m_r + 0.10, m_y, "Bơm\n5V", fontsize=8.0, fontweight='bold', ha='left', va='center', zorder=10)

    # ==========================================================
    # CLEAN LEGEND BAR AT BOTTOM (2 lines inside border)
    # ==========================================================
    ax.plot([0.45, 17.35], [0.85, 0.85], color='#000000', lw=0.8)
    legend_line1 = (
        "Chú thích ký hiệu chuẩn IEC:   "
        "[S1] Công tắc nguồn chính   |   "
        "[F1, F2] Cầu chì bảo vệ quá dòng   |   "
        "[R1, R2] Cầu phân áp Echo (5V → 3.3V)   |   "
        "[R3–R6] Điện trở hạn dòng LED & Còi"
    )
    legend_line2 = (
        "[H1–H3] Đèn LED chỉ thị trạng thái   |   "
        "[BZ] Còi báo động 5V   |   "
        "[C1] Tụ lọc nguồn Servo   |   "
        "[K1] Cuộn hút & Tiếp điểm Relay (Active LOW)   |   "
        "[D1] Diode dập xung ngược   |   "
        "[M] Máy bơm 5V"
    )
    ax.text(8.90, 0.63, legend_line1, fontsize=7.5, ha='center', va='center', zorder=10)
    ax.text(8.90, 0.40, legend_line2, fontsize=7.5, ha='center', va='center', zorder=10)

    for d in out_dirs:
        filepath = os.path.join(d, "circuit_diagram.png")
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass
        fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='#ffffff')
    plt.close(fig)
    print("Generated clean B&W IEC circuit_diagram.png successfully!")


if __name__ == "__main__":
    create_circuit_diagram()
