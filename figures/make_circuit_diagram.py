import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os

out_dirs = [
    os.path.join("d:\\1. project\\FloodGuard", "figures"),
    os.path.join("d:\\1. project\\FloodGuard", "report", "figures")
]
for d in out_dirs:
    os.makedirs(d, exist_ok=True)

# Styling for crisp presentation
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['text.color'] = '#0f172a'

def create_circuit_diagram():
    fig, ax = plt.subplots(figsize=(20.0, 11.25), dpi=300)
    ax.set_xlim(0, 20.0)
    ax.set_ylim(0, 11.25)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Main outer frame
    bg_frame = FancyBboxPatch((0.3, 0.3), 19.4, 10.65, boxstyle="round,pad=0.08,rounding_size=0.15",
                              facecolor='#f8fafc', edgecolor='#cbd5e1', lw=1.5, zorder=0)
    ax.add_patch(bg_frame)

    # ==========================================
    # HEADER SECTION (MINIMALIST & CLEAN)
    # ==========================================
    title_box = FancyBboxPatch((0.6, 10.35), 18.8, 0.50, boxstyle="round,pad=0.06,rounding_size=0.12",
                               facecolor='#0f172a', edgecolor='none', zorder=2)
    ax.add_patch(title_box)
    ax.text(10.0, 10.65, "SƠ ĐỒ NỐI DÂY PHẦN CỨNG & CÁC CHÂN GPIO - HỆ THỐNG FLOODGUARD",
            fontsize=13.5, fontweight='bold', color='#ffffff', ha='center', va='center', zorder=3)
    ax.text(10.0, 10.45, "ESP32 DevKit V1 | Điều Khiển Máy Bơm Qua Relay 5V (Active LOW) | Cảm Biến Siêu Âm, Mưa, Servo & Cảnh Báo",
            fontsize=8.5, style='italic', color='#94a3b8', ha='center', va='center', zorder=3)

    # Helper: draw pin terminal
    def draw_terminal(px, py, label="", color='#0f172a', text_color='#ffffff', radius=0.14, font_size=7.0):
        circle = plt.Circle((px, py), radius, facecolor=color, edgecolor='#334155', lw=1.0, zorder=12)
        ax.add_patch(circle)
        if label:
            ax.text(px, py, label, fontsize=font_size, fontweight='bold', color=text_color, ha='center', va='center', zorder=13)

    # Helper: draw wire
    def draw_wire(pts, color='#2563eb', lw=2.2, style='-', zorder=4):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax.plot(xs, ys, color=color, lw=lw, linestyle=style, zorder=zorder, solid_capstyle='round', solid_joinstyle='round')

    # Helper: module card box
    def draw_card(x, y, w, h, title, border_color='#0ea5e9', bg_color='#ffffff'):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.15",
                             facecolor=bg_color, edgecolor=border_color, lw=1.8, zorder=2)
        ax.add_patch(box)
        th = 0.38
        tbox = FancyBboxPatch((x, y + h - th), w, th, boxstyle="round,pad=0.06,rounding_size=0.12",
                              facecolor=border_color, edgecolor='none', zorder=3)
        ax.add_patch(tbox)
        ax.text(x + w/2, y + h - th/2, title, fontsize=9.0, fontweight='bold', color='#ffffff',
                ha='center', va='center', zorder=4)

    # ==========================================
    # 1. ESP32 DEVKIT V1 (CENTER COLUMN)
    # ==========================================
    esp_x, esp_y, esp_w, esp_h = 8.2, 3.4, 3.6, 6.2
    pcb = FancyBboxPatch((esp_x, esp_y), esp_w, esp_h, boxstyle="round,pad=0.08,rounding_size=0.2",
                         facecolor='#0f172a', edgecolor='#38bdf8', lw=2.2, zorder=2)
    ax.add_patch(pcb)

    # Header
    ax.text(esp_x + esp_w/2, esp_y + esp_h - 0.4, "ESP32 DEVKIT V1", fontsize=11.5,
            fontweight='bold', color='#38bdf8', ha='center', va='center', zorder=4)
    ax.text(esp_x + esp_w/2, esp_y + esp_h - 0.68, "Microcontroller (3.3V Logic)", fontsize=7.2,
            style='italic', color='#94a3b8', ha='center', va='center', zorder=4)

    # Metal Shield
    shield = FancyBboxPatch((esp_x + 0.5, esp_y + 2.1), 2.6, 2.6, boxstyle="round,pad=0.04,rounding_size=0.1",
                            facecolor='#1e293b', edgecolor='#94a3b8', lw=1.2, zorder=3)
    ax.add_patch(shield)
    ax.text(esp_x + esp_w/2, esp_y + 3.7, "ESP-WROOM-32", fontsize=9.5, fontweight='bold', color='#f8fafc', ha='center', va='center', zorder=4)
    ax.text(esp_x + esp_w/2, esp_y + 3.1, "Wi-Fi & Bluetooth\nDual-Core Xtensa", fontsize=7.2, color='#cbd5e1', ha='center', va='center', zorder=4)

    # USB Connector
    usb = FancyBboxPatch((esp_x + esp_w/2 - 0.5, esp_y - 0.12), 1.0, 0.4, boxstyle="round,pad=0.02,rounding_size=0.05",
                         facecolor='#cbd5e1', edgecolor='#475569', lw=1.2, zorder=3)
    ax.add_patch(usb)
    ax.text(esp_x + esp_w/2, esp_y + 0.1, "USB (5V IN)", fontsize=6.8, fontweight='bold', color='#1e293b', ha='center', va='center', zorder=4)

    # Spaced Active Pins on ESP32
    # Left Header: 7 pins
    left_pins = [
        ("3V3", 8.8, "#ea580c"),
        ("D34 (DO)", 8.0, "#0284c7"),
        ("D35 (AO)", 7.2, "#0284c7"),
        ("D27 (PWM)", 6.4, "#d97706"),
        ("D12 (ECHO)", 5.6, "#059669"),
        ("D13 (TRIG)", 4.8, "#2563eb"),
        ("GND", 4.0, "#1e293b")
    ]
    esp_left_pts = {}
    for name, py, col in left_pins:
        px = esp_x + 0.18
        plt.plot(px, py, 'o', color='#f8fafc', markersize=5.0, zorder=5)
        ax.text(px + 0.22, py, name, fontsize=7.2, fontweight='bold', color='#f8fafc', ha='left', va='center', zorder=5)
        esp_left_pts[name.split()[0]] = (px, py)

    # Right Header: 7 pins
    right_pins = [
        ("VIN (5V)", 8.8, "#dc2626"),
        ("GND", 8.0, "#1e293b"),
        ("D23 (RELAY)", 7.2, "#7c3aed"),
        ("D4 (BUZZ)", 6.4, "#0891b2"),
        ("D21 (LED-G)", 5.6, "#16a34a"),
        ("D19 (LED-Y)", 4.8, "#ca8a04"),
        ("D18 (LED-R)", 4.0, "#e11d48")
    ]
    esp_right_pts = {}
    for name, py, col in right_pins:
        px = esp_x + esp_w - 0.18
        plt.plot(px, py, 'o', color='#f8fafc', markersize=5.0, zorder=5)
        ax.text(px - 0.22, py, name, fontsize=7.2, fontweight='bold', color='#f8fafc', ha='right', va='center', zorder=5)
        esp_right_pts[name.split()[0]] = (px, py)


    # ==========================================
    # 2. KHỐI CẢM BIẾN (LEFT COLUMN)
    # ==========================================
    # 2.1 Cảm biến siêu âm HC-SR04
    draw_card(0.6, 6.7, 4.4, 2.7, "CẢM BIẾN SIÊU ÂM (HC-SR04)", '#2563eb')
    # Transducers
    ax.add_patch(plt.Circle((1.8, 7.9), 0.55, facecolor='#e2e8f0', edgecolor='#1e293b', lw=1.5, zorder=4))
    ax.add_patch(plt.Circle((3.8, 7.9), 0.55, facecolor='#e2e8f0', edgecolor='#1e293b', lw=1.5, zorder=4))
    ax.text(1.8, 7.9, "T\n(Phát)", fontsize=7.5, fontweight='bold', color='#0f172a', ha='center', va='center', zorder=5)
    ax.text(3.8, 7.9, "R\n(Thu)", fontsize=7.5, fontweight='bold', color='#0f172a', ha='center', va='center', zorder=5)
    
    # HC-SR04 Terminals (Right side of card)
    sr_vcc  = (4.75, 8.8)
    sr_echo = (4.75, 8.0)
    sr_trig = (4.75, 7.3)
    sr_gnd  = (4.75, 6.7)
    draw_terminal(sr_vcc[0], sr_vcc[1], "VCC", "#dc2626")
    draw_terminal(sr_echo[0], sr_echo[1], "ECHO", "#059669")
    draw_terminal(sr_trig[0], sr_trig[1], "TRIG", "#2563eb")
    draw_terminal(sr_gnd[0], sr_gnd[1], "GND", "#1e293b")

    # 2.2 Cảm biến mưa (Rain Sensor)
    draw_card(0.6, 3.4, 4.4, 2.7, "CẢM BIẾN MƯA (RAIN SENSOR)", '#0284c7')
    # Sensing board
    plate = FancyBboxPatch((1.0, 4.1), 1.8, 1.3, boxstyle="square,pad=0.02",
                           facecolor='#e2e8f0', edgecolor='#0284c7', lw=1.2, zorder=4)
    ax.add_patch(plate)
    for yy in np.linspace(4.25, 5.25, 5):
        ax.plot([1.15, 2.65], [yy, yy], color='#0284c7', lw=1.5, zorder=5)
    ax.text(1.9, 3.75, "Tấm Điện Cực Mưa", fontsize=6.8, style='italic', color='#475569', ha='center', va='center', zorder=5)

    # LM393 chip
    comp = FancyBboxPatch((3.1, 4.2), 1.5, 1.1, boxstyle="round,pad=0.03",
                          facecolor='#1e293b', edgecolor='#64748b', lw=1.0, zorder=4)
    ax.add_patch(comp)
    ax.text(3.85, 4.75, "LM393\nModule", fontsize=7.2, fontweight='bold', color='#f8fafc', ha='center', va='center', zorder=5)

    # Terminals
    rain_vcc = (4.75, 5.7)
    rain_ao  = (4.75, 5.0)
    rain_do  = (4.75, 4.3)
    rain_gnd = (4.75, 3.6)
    draw_terminal(rain_vcc[0], rain_vcc[1], "VCC", "#ea580c")
    draw_terminal(rain_ao[0], rain_ao[1], "AO", "#0284c7")
    draw_terminal(rain_do[0], rain_do[1], "DO", "#0284c7")
    draw_terminal(rain_gnd[0], rain_gnd[1], "GND", "#1e293b")


    # ==========================================
    # 3. KHỐI CHẤP HÀNH (RIGHT COLUMN)
    # ==========================================
    # 3.1 Module Relay 5V & Máy Bơm Mini
    draw_card(14.8, 6.7, 4.6, 2.7, "MODULE RELAY 5V & MÁY BƠM", '#7c3aed')
    
    # Relay Blue Cube
    cube = FancyBboxPatch((15.2, 7.3), 1.7, 1.3, boxstyle="round,pad=0.04",
                          facecolor='#2563eb', edgecolor='#1e293b', lw=1.4, zorder=4)
    ax.add_patch(cube)
    ax.text(16.05, 8.15, "RELAY 5V", fontsize=8.5, fontweight='bold', color='#ffffff', ha='center', va='center', zorder=5)
    ax.text(16.05, 7.65, "SRD-05VDC\nActive LOW", fontsize=6.8, color='#bfdbfe', ha='center', va='center', zorder=5)

    # Relay Input Terminals (Left)
    rel_vcc = (15.0, 8.8)
    rel_in  = (15.0, 7.8)
    rel_gnd = (15.0, 6.9)
    draw_terminal(rel_vcc[0], rel_vcc[1], "VCC", "#dc2626")
    draw_terminal(rel_in[0], rel_in[1], "IN", "#7c3aed")
    draw_terminal(rel_gnd[0], rel_gnd[1], "GND", "#1e293b")

    # Output Screw Terminals (Right)
    ax.text(17.2, 8.45, "NO (Tiếp điểm mở)", fontsize=6.8, fontweight='bold', color='#dc2626', ha='left', va='center', zorder=5)
    ax.text(17.2, 7.85, "COM (Nguồn 5V)", fontsize=6.8, fontweight='bold', color='#1e293b', ha='left', va='center', zorder=5)

    # Mini Water Pump
    pump_box = FancyBboxPatch((17.6, 6.85), 1.5, 0.65, boxstyle="round,pad=0.03",
                              facecolor='#f1f5f9', edgecolor='#7c3aed', lw=1.5, zorder=4)
    ax.add_patch(pump_box)
    ax.text(18.35, 7.17, "MÁY BƠM\n5V MINI", fontsize=7.0, fontweight='bold', color='#0f172a', ha='center', va='center', zorder=5)

    # Connect NO to Pump (+) and COM to 5V Source
    draw_wire([(17.1, 8.2), (18.6, 8.2), (18.6, 7.5)], color='#dc2626', lw=2.0)
    # Pump (-) to Relay GND
    draw_wire([(18.0, 6.85), (18.0, 6.55), (15.0, 6.55), (15.0, 6.75)], color='#1e293b', lw=1.8)
    # External 5V into COM
    draw_wire([(17.1, 7.6), (17.3, 7.6)], color='#dc2626', lw=1.8, style='--')

    # 3.2 Động cơ Servo SG90 (Van Thoát Lũ)
    draw_card(14.8, 3.4, 4.6, 2.7, "ĐỘNG CƠ SERVO SG90", '#d97706')
    
    # Servo Body
    servo = FancyBboxPatch((15.2, 4.1), 2.0, 1.2, boxstyle="round,pad=0.05",
                           facecolor='#0284c7', edgecolor='#0369a1', lw=1.5, zorder=4)
    ax.add_patch(servo)
    ax.text(16.2, 4.85, "SG90 Micro Servo", fontsize=7.5, fontweight='bold', color='#ffffff', ha='center', va='center', zorder=5)
    ax.text(16.2, 4.45, "Góc 0° - 90° - 180°", fontsize=7.0, color='#bae6fd', ha='center', va='center', zorder=5)

    # Rotating arm
    horn = patches.Wedge((17.8, 4.7), 0.45, -45, 135, facecolor='#ffffff', edgecolor='#0f172a', lw=1.2, zorder=6)
    ax.add_patch(horn)
    ax.plot([17.8, 18.5], [4.7, 5.15], color='#e11d48', lw=2.8, zorder=7)
    ax.text(18.6, 4.4, "Cánh Van", fontsize=7.0, fontweight='bold', color='#e11d48', ha='center', va='center', zorder=8)

    # Servo Terminals (Left)
    servo_pwm = (15.0, 5.4)
    servo_vcc = (15.0, 4.6)
    servo_gnd = (15.0, 3.8)
    draw_terminal(servo_pwm[0], servo_pwm[1], "PWM", "#d97706")
    draw_terminal(servo_vcc[0], servo_vcc[1], "5V", "#dc2626")
    draw_terminal(servo_gnd[0], servo_gnd[1], "GND", "#1e293b")


    # ==========================================
    # 4. KHỐI CẢNH BÁO TẠI CHỖ (BOTTOM: 4 CARDS)
    # Height lowered to 1.45 (top at y = 1.95), leaving y=1.95 to 3.4 pure corridor!
    # Terminals placed cleanly at the top of card body (y = 1.95)!
    # ==========================================
    card_y = 0.50
    card_h = 1.45
    card_w = 4.2
    gap = 0.45
    term_y = card_y + card_h  # Exactly at the top edge of the card

    # 4.1 Còi Buzzer 5V
    bx = 0.6
    draw_card(bx, card_y, card_w, card_h, "CÒI BUZZER 5V", '#0891b2')
    ax.add_patch(plt.Circle((bx + card_w/2, card_y + 0.55), 0.32, facecolor='#1e293b', edgecolor='#0891b2', lw=1.5, zorder=4))
    ax.text(bx + card_w/2, card_y + 0.55, "+\nBUZZ", fontsize=7.2, fontweight='bold', color='#ffffff', ha='center', va='center', zorder=5)
    buz_sig = (bx + 1.1, term_y)
    buz_gnd = (bx + card_w - 1.1, term_y)
    draw_terminal(buz_sig[0], buz_sig[1], "D4", "#0891b2")
    draw_terminal(buz_gnd[0], buz_gnd[1], "GND", "#1e293b")

    # 4.2 LED Xanh (NORMAL)
    gx = bx + card_w + gap
    draw_card(gx, card_y, card_w, card_h, "LED XANH (NORMAL <40%)", '#16a34a')
    ax.add_patch(plt.Circle((gx + card_w/2 - 0.7, card_y + 0.55), 0.26, facecolor='#22c55e', edgecolor='#15803d', lw=1.5, zorder=4))
    ax.text(gx + card_w/2 - 0.7, card_y + 0.55, "LED", fontsize=6.8, fontweight='bold', color='#ffffff', ha='center', va='center', zorder=5)
    ax.add_patch(FancyBboxPatch((gx + card_w/2 + 0.1, card_y + 0.42), 1.2, 0.26, boxstyle="square,pad=0.02",
                                facecolor='#cbd5e1', edgecolor='#475569', lw=1.0, zorder=4))
    ax.text(gx + card_w/2 + 0.7, card_y + 0.55, "220 Ω", fontsize=6.8, fontweight='bold', color='#0f172a', ha='center', va='center', zorder=5)
    led_g_sig = (gx + 1.1, term_y)
    led_g_gnd = (gx + card_w - 1.1, term_y)
    draw_terminal(led_g_sig[0], led_g_sig[1], "D21", "#16a34a")
    draw_terminal(led_g_gnd[0], led_g_gnd[1], "GND", "#1e293b")

    # 4.3 LED Vàng (WARNING)
    yx = gx + card_w + gap
    draw_card(yx, card_y, card_w, card_h, "LED VÀNG (WARNING 41-70%)", '#ca8a04')
    ax.add_patch(plt.Circle((yx + card_w/2 - 0.7, card_y + 0.55), 0.26, facecolor='#eab308', edgecolor='#a16207', lw=1.5, zorder=4))
    ax.text(yx + card_w/2 - 0.7, card_y + 0.55, "LED", fontsize=6.8, fontweight='bold', color='#ffffff', ha='center', va='center', zorder=5)
    ax.add_patch(FancyBboxPatch((yx + card_w/2 + 0.1, card_y + 0.42), 1.2, 0.26, boxstyle="square,pad=0.02",
                                facecolor='#cbd5e1', edgecolor='#475569', lw=1.0, zorder=4))
    ax.text(yx + card_w/2 + 0.7, card_y + 0.55, "220 Ω", fontsize=6.8, fontweight='bold', color='#0f172a', ha='center', va='center', zorder=5)
    led_y_sig = (yx + 1.1, term_y)
    led_y_gnd = (yx + card_w - 1.1, term_y)
    draw_terminal(led_y_sig[0], led_y_sig[1], "D19", "#ca8a04")
    draw_terminal(led_y_gnd[0], led_y_gnd[1], "GND", "#1e293b")

    # 4.4 LED Đỏ (CRITICAL)
    rx = yx + card_w + gap
    draw_card(rx, card_y, card_w, card_h, "LED ĐỎ (CRITICAL >70%)", '#e11d48')
    ax.add_patch(plt.Circle((rx + card_w/2 - 0.7, card_y + 0.55), 0.26, facecolor='#ef4444', edgecolor='#b91c1c', lw=1.5, zorder=4))
    ax.text(rx + card_w/2 - 0.7, card_y + 0.55, "LED", fontsize=6.8, fontweight='bold', color='#ffffff', ha='center', va='center', zorder=5)
    ax.add_patch(FancyBboxPatch((rx + card_w/2 + 0.1, card_y + 0.42), 1.2, 0.26, boxstyle="square,pad=0.02",
                                facecolor='#cbd5e1', edgecolor='#475569', lw=1.0, zorder=4))
    ax.text(rx + card_w/2 + 0.7, card_y + 0.55, "220 Ω", fontsize=6.8, fontweight='bold', color='#0f172a', ha='center', va='center', zorder=5)
    led_r_sig = (rx + 1.1, term_y)
    led_r_gnd = (rx + card_w - 1.1, term_y)
    draw_terminal(led_r_sig[0], led_r_sig[1], "D18", "#e11d48")
    draw_terminal(led_r_gnd[0], led_r_gnd[1], "GND", "#1e293b")


    # ==========================================
    # 5. WIRING CONNECTIONS (SPACIOUS & CLEAR)
    # ==========================================
    # --- SENSORS TO ESP32 (LEFT CORRIDOR: x = 5.0 to 8.2) ---
    # Wire 1: HC-SR04 TRIG -> ESP32 D13
    draw_wire([sr_trig, (6.1, sr_trig[1]), (6.1, esp_left_pts["D13"][1]), esp_left_pts["D13"]], color='#2563eb', lw=2.2)
    ax.text(6.2, 7.3, "Trig (D13)", fontsize=7.2, fontweight='bold', color='#2563eb', zorder=8)

    # Wire 2: HC-SR04 ECHO -> ESP32 D12
    draw_wire([sr_echo, (6.5, sr_echo[1]), (6.5, esp_left_pts["D12"][1]), esp_left_pts["D12"]], color='#059669', lw=2.2)
    ax.text(6.6, 7.8, "Echo (D12)", fontsize=7.2, fontweight='bold', color='#059669', zorder=8)

    # Wire 3: Rain AO -> ESP32 D35
    draw_wire([rain_ao, (6.9, rain_ao[1]), (6.9, esp_left_pts["D35"][1]), esp_left_pts["D35"]], color='#0284c7', lw=2.2)
    ax.text(7.0, 6.8, "Rain AO (D35)", fontsize=7.2, fontweight='bold', color='#0284c7', zorder=8)

    # Wire 4: Rain DO -> ESP32 D34
    draw_wire([rain_do, (7.3, rain_do[1]), (7.3, esp_left_pts["D34"][1]), esp_left_pts["D34"]], color='#0284c7', lw=1.8, style='--')
    ax.text(7.4, 4.3, "Rain DO (D34)", fontsize=6.8, style='italic', color='#0284c7', zorder=8)

    # Wire 5: ESP32 D27 -> Servo PWM (Dây cam)
    draw_wire([esp_left_pts["D27"], (7.7, esp_left_pts["D27"][1]), (7.7, 3.0), (14.2, 3.0), (14.2, servo_pwm[1]), servo_pwm], color='#d97706', lw=2.2)
    ax.text(12.7, 3.12, "PWM D27 (Servo SG90)", fontsize=7.2, fontweight='bold', color='#d97706', zorder=8)


    # --- ACTUATORS TO ESP32 (RIGHT CORRIDOR: x = 11.8 to 14.8) ---
    # Wire 6: ESP32 D23 -> Relay IN (Active LOW)
    draw_wire([esp_right_pts["D23"], (13.6, esp_right_pts["D23"][1]), (13.6, rel_in[1]), rel_in], color='#7c3aed', lw=2.5)
    ax.text(13.7, 7.5, "Relay IN (D23)\n[Active LOW]", fontsize=7.5, fontweight='bold', color='#7c3aed', zorder=8)


    # --- SIGNALING TO ESP32 (BOTTOM CORRIDOR: y = 2.0 to 3.4) ---
    # Completely above card headers! Clean horizontal tracks, drop down into terminals!
    # Wire 7: ESP32 D4 -> Buzzer (D4)
    draw_wire([esp_right_pts["D4"], (12.2, esp_right_pts["D4"][1]), (12.2, 2.75), (buz_sig[0], 2.75), buz_sig], color='#0891b2', lw=2.0)
    ax.text(buz_sig[0] + 0.2, 2.85, "Buzzer (D4)", fontsize=7.0, fontweight='bold', color='#0891b2', zorder=8)

    # Wire 8: ESP32 D21 -> LED Green (D21)
    draw_wire([esp_right_pts["D21"], (12.5, esp_right_pts["D21"][1]), (12.5, 2.55), (led_g_sig[0], 2.55), led_g_sig], color='#16a34a', lw=2.0)
    ax.text(led_g_sig[0] + 0.2, 2.65, "LED-G (D21)", fontsize=7.0, fontweight='bold', color='#16a34a', zorder=8)

    # Wire 9: ESP32 D19 -> LED Yellow (D19)
    draw_wire([esp_right_pts["D19"], (12.8, esp_right_pts["D19"][1]), (12.8, 2.35), (led_y_sig[0], 2.35), led_y_sig], color='#ca8a04', lw=2.0)
    ax.text(led_y_sig[0] + 0.2, 2.45, "LED-Y (D19)", fontsize=7.0, fontweight='bold', color='#ca8a04', zorder=8)

    # Wire 10: ESP32 D18 -> LED Red (D18)
    draw_wire([esp_right_pts["D18"], (13.1, esp_right_pts["D18"][1]), (13.1, 2.15), (led_r_sig[0], 2.15), led_r_sig], color='#e11d48', lw=2.0)
    ax.text(led_r_sig[0] - 1.0, 2.25, "LED-R (D18)", fontsize=7.0, fontweight='bold', color='#e11d48', zorder=8)


    # --- POWER BUS ROUTING (5V, 3.3V, GND) ---
    # 5V VBUS Rail (Red) -> feeds Relay, Servo, and HC-SR04
    draw_wire([esp_right_pts["VIN"], (14.4, esp_right_pts["VIN"][1]), rel_vcc], color='#dc2626', lw=2.0) # To Relay VCC
    draw_wire([(14.4, esp_right_pts["VIN"][1]), (14.4, servo_vcc[1]), servo_vcc], color='#dc2626', lw=1.8) # To Servo 5V
    draw_wire([(esp_right_pts["VIN"][0], esp_right_pts["VIN"][1]), (11.8, 9.6), (5.5, 9.6), (5.5, sr_vcc[1]), sr_vcc], color='#dc2626', lw=1.8, style=':') # To HC-SR04 VCC
    ax.text(13.5, 8.95, "5V (VIN)", fontsize=7.0, fontweight='bold', color='#dc2626', zorder=8)

    # 3.3V Rail (Orange) from Left Header directly down corridor to Rain Sensor
    draw_wire([esp_left_pts["3V3"], (5.7, esp_left_pts["3V3"][1]), (5.7, rain_vcc[1]), rain_vcc], color='#ea580c', lw=1.8, style=':')
    ax.text(5.9, 6.0, "3.3V", fontsize=7.0, fontweight='bold', color='#ea580c', zorder=8)

    # Common GND Rail:
    # Right Header GND feeds Relay & Servo
    draw_wire([esp_right_pts["GND"], (14.0, esp_right_pts["GND"][1]), (14.0, rel_gnd[1]), rel_gnd], color='#1e293b', lw=2.0)
    draw_wire([(14.0, rel_gnd[1]), (14.0, servo_gnd[1]), servo_gnd], color='#1e293b', lw=1.8)
    ax.text(13.5, 8.15, "GND", fontsize=7.0, fontweight='bold', color='#1e293b', zorder=8)

    # Left Header GND feeds HC-SR04, Rain Sensor, and Bottom cards
    draw_wire([esp_left_pts["GND"], (5.2, esp_left_pts["GND"][1]), (5.2, sr_gnd[1]), sr_gnd], color='#1e293b', lw=1.6, style=':')
    draw_wire([(5.2, esp_left_pts["GND"][1]), (5.2, rain_gnd[1]), rain_gnd], color='#1e293b', lw=1.6, style=':')
    # Ground wire cleanly running horizontally above cards at y = 2.05, dropping to each GND terminal!
    draw_wire([(5.2, esp_left_pts["GND"][1]), (5.2, 2.05), (buz_gnd[0], 2.05), buz_gnd], color='#1e293b', lw=1.5, style=':')
    draw_wire([(buz_gnd[0], 2.05), (led_g_gnd[0], 2.05), led_g_gnd], color='#1e293b', lw=1.5, style=':')
    draw_wire([(led_g_gnd[0], 2.05), (led_y_gnd[0], 2.05), led_y_gnd], color='#1e293b', lw=1.5, style=':')
    draw_wire([(led_y_gnd[0], 2.05), (led_r_gnd[0], 2.05), led_r_gnd], color='#1e293b', lw=1.5, style=':')


    # ==========================================
    # 6. TECHNICAL NOTE (HIGH-Z RELAY 5V)
    # ==========================================
    callout = FancyBboxPatch((7.0, 9.80), 6.0, 0.35, boxstyle="round,pad=0.04,rounding_size=0.08",
                             facecolor='#fef3c7', edgecolor='#f59e0b', lw=1.2, zorder=8)
    ax.add_patch(callout)
    ax.text(10.0, 9.97, "⚡ Lưu ý Relay Active LOW (D23): Dùng High-Z (pinMode INPUT để ngắt) triệt tiêu rò dòng 3.3V-5V",
            fontsize=7.2, fontweight='bold', color='#b45309', ha='center', va='center', zorder=9)

    # Save to both folders
    plt.tight_layout()
    for d in out_dirs:
        out_path = os.path.join(d, "circuit_diagram.png")
        fig.savefig(out_path, dpi=300, bbox_inches='tight')
        print(f"Generated Circuit Diagram: {out_path}")
    plt.close(fig)

if __name__ == "__main__":
    print("Creating FloodGuard simplified, spacious circuit diagram...")
    create_circuit_diagram()
    print("Done!")
