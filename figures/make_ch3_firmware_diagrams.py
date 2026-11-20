import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Polygon, Arc

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#000000'
plt.rcParams['axes.linewidth'] = 1.3
plt.rcParams['text.color'] = '#000000'

def draw_sensor_icon(ax, x, y, kind='ultrasonic'):
    """Vẽ icon vector đen trắng sắc nét không phụ thuộc vào font emoji hệ thống"""
    if kind == 'ultrasonic':
        ax.plot([x - 0.12, x - 0.12], [y - 0.18, y + 0.18], color='#000000', lw=2.2, zorder=6)
        arc1 = Arc((x - 0.10, y), 0.22, 0.22, angle=0, theta1=-45, theta2=45, color='#000000', lw=1.8, zorder=6)
        arc2 = Arc((x - 0.10, y), 0.38, 0.38, angle=0, theta1=-45, theta2=45, color='#333333', lw=1.8, zorder=6)
        arc3 = Arc((x - 0.10, y), 0.54, 0.54, angle=0, theta1=-45, theta2=45, color='#555555', lw=1.8, zorder=6)
        ax.add_patch(arc1)
        ax.add_patch(arc2)
        ax.add_patch(arc3)
    elif kind == 'rain':
        c1 = Circle((x - 0.08, y + 0.04), 0.10, facecolor='#d1d5db', edgecolor='#000000', lw=1.2, zorder=6)
        c2 = Circle((x + 0.06, y + 0.06), 0.12, facecolor='#d1d5db', edgecolor='#000000', lw=1.2, zorder=6)
        c3 = Circle((x + 0.18, y + 0.02), 0.08, facecolor='#d1d5db', edgecolor='#000000', lw=1.2, zorder=6)
        base = FancyBboxPatch((x - 0.14, y - 0.05), 0.36, 0.12, boxstyle="round,pad=0.02,rounding_size=0.05",
                              facecolor='#d1d5db', edgecolor='#000000', lw=1.2, zorder=6)
        ax.add_patch(base)
        ax.add_patch(c1)
        ax.add_patch(c2)
        ax.add_patch(c3)
        for dx, dy in [(-0.10, -0.16), (0.02, -0.19), (0.14, -0.16)]:
            ax.plot([x + dx - 0.02, x + dx], [y + dy + 0.06, y + dy], color='#000000', lw=1.6, zorder=6)


def create_firmware_modules_diagram(output_paths):
    fig, ax = plt.subplots(figsize=(10.8, 8.8), dpi=300)
    ax.set_xlim(0, 12.0)
    ax.set_ylim(0, 9.6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Monochrome Palette
    c_box_fill = '#f3f4f6'
    c_box_border = '#111827'
    c_text_dark = '#000000'
    c_text_muted = '#374151'
    c_arrow = '#000000'
    c_badge = '#111827'

    # Container coordinates
    cont_x = 2.30
    cont_w = 6.40
    cont_right = cont_x + cont_w  # 8.70
    cont_center = cont_x + cont_w / 2.0  # 5.50

    # 1. Outer dashed container for ESP32 FIRMWARE
    dashed_box = FancyBboxPatch((cont_x, 0.25), cont_w, 8.55,
                                boxstyle="round,pad=0.08,rounding_size=0.25",
                                facecolor='#fafafa', edgecolor='#4b5563',
                                linestyle='--', linewidth=1.8, zorder=1)
    ax.add_patch(dashed_box)

    # ESP32 FIRMWARE Title header
    header_w = 3.20
    header_box = FancyBboxPatch((cont_center - header_w / 2.0, 8.52), header_w, 0.58,
                                boxstyle="round,pad=0.06,rounding_size=0.15",
                                facecolor='#e5e7eb', edgecolor='#111827',
                                linewidth=2.0, zorder=10)
    ax.add_patch(header_box)
    ax.text(cont_center, 8.81, 'ESP32 FIRMWARE', fontsize=12.5, fontweight='bold',
            ha='center', va='center', color=c_text_dark, zorder=11)

    # 2. External Sensors on the left
    # Sensor 1: HC-SR04
    s1_box = FancyBboxPatch((0.25, 6.95), 1.70, 0.95,
                            boxstyle="round,pad=0.06,rounding_size=0.15",
                            facecolor=c_box_fill, edgecolor=c_box_border,
                            linewidth=1.6, zorder=2)
    ax.add_patch(s1_box)
    draw_sensor_icon(ax, 0.55, 7.42, kind='ultrasonic')
    ax.text(1.30, 7.55, 'HC-SR04', fontsize=9.5, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)
    ax.text(1.30, 7.25, '(Khoảng cách)', fontsize=8.0, ha='center', va='center', color=c_text_muted, zorder=10)

    # Sensor 2: FC-37
    s2_box = FancyBboxPatch((0.25, 5.75), 1.70, 0.95,
                            boxstyle="round,pad=0.06,rounding_size=0.15",
                            facecolor=c_box_fill, edgecolor=c_box_border,
                            linewidth=1.6, zorder=2)
    ax.add_patch(s2_box)
    draw_sensor_icon(ax, 0.55, 6.22, kind='rain')
    ax.text(1.30, 6.35, 'FC-37', fontsize=9.5, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)
    ax.text(1.30, 6.05, '(Mưa)', fontsize=8.0, ha='center', va='center', color=c_text_muted, zorder=10)

    # Blocks definition
    b_left = 3.25
    b_width = 5.00
    b_right = b_left + b_width  # 8.25
    b_center = b_left + b_width / 2.0  # 5.75

    # Sensor connecting lines to Block 1 and Block 2
    ax.plot([1.95, 2.12], [7.42, 7.42], color=c_arrow, lw=1.6, zorder=3)
    ax.plot([1.95, 2.12], [6.22, 6.22], color=c_arrow, lw=1.6, zorder=3)
    ax.plot([2.12, 2.12], [6.22, 7.70], color=c_arrow, lw=1.6, zorder=3)
    # Arrow to Block 1
    ax.annotate('', xy=(b_left, 7.70), xytext=(2.12, 7.70),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)
    # Arrow to Block 2
    ax.annotate('', xy=(b_left, 6.55), xytext=(2.12, 6.55),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)

    # 3. Internal Blocks (1 to 7)
    def draw_badge(x, y, num):
        badge = Circle((x, y), 0.17, facecolor=c_badge, edgecolor='#000000', lw=1.0, zorder=7)
        ax.add_patch(badge)
        ax.text(x, y, str(num), fontsize=8.5, fontweight='bold', ha='center', va='center', color='#ffffff', zorder=8)

    # Block 1: Sensor Processing
    b1_y = 7.70
    b1 = FancyBboxPatch((b_left, b1_y - 0.40), b_width, 0.80,
                        boxstyle="round,pad=0.06,rounding_size=0.15",
                        facecolor=c_box_fill, edgecolor=c_box_border, lw=1.6, zorder=5)
    ax.add_patch(b1)
    draw_badge(b_left + 0.35, b1_y, 1)
    ax.text(b_center + 0.15, b1_y + 0.14, 'Sensor Processing', fontsize=10.5, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)
    ax.text(b_center + 0.15, b1_y - 0.16, '(HC-SR04 distance; FC-37 rain AO/DO)', fontsize=8.2, ha='center', va='center', color=c_text_muted, zorder=10)

    # Block 2: Median-of-3 Filter
    b2_y = 6.55
    b2 = FancyBboxPatch((b_left, b2_y - 0.40), b_width, 0.80,
                        boxstyle="round,pad=0.06,rounding_size=0.15",
                        facecolor=c_box_fill, edgecolor=c_box_border, lw=1.6, zorder=5)
    ax.add_patch(b2)
    draw_badge(b_left + 0.35, b2_y, 2)
    ax.text(b_center + 0.15, b2_y + 0.14, 'Median-of-3 Filter', fontsize=10.5, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)
    ax.text(b_center + 0.15, b2_y - 0.16, '(remove outlier noise)', fontsize=8.2, ha='center', va='center', color=c_text_muted, zorder=10)

    # Arrow 1 -> 2
    ax.annotate('', xy=(b_center, b2_y + 0.40), xytext=(b_center, b1_y - 0.40),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)

    # Block 3: FSM Core + Hysteresis
    b3_y = 5.25
    b3 = FancyBboxPatch((b_left, b3_y - 0.48), b_width, 0.96,
                        boxstyle="round,pad=0.06,rounding_size=0.15",
                        facecolor=c_box_fill, edgecolor=c_box_border, lw=1.6, zorder=5)
    ax.add_patch(b3)
    draw_badge(b_left + 0.35, b3_y + 0.12, 3)
    ax.text(b_center + 0.15, b3_y + 0.18, 'FSM Core + Hysteresis', fontsize=10.5, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)
    ax.text(b_center + 0.15, b3_y - 0.16, '(NORMAL / WARNING / DANGER / CRITICAL;\nSENSOR_FAULT)',
            fontsize=8.0, ha='center', va='center', color=c_text_muted, multialignment='center', zorder=10)

    # Arrow 2 -> 3
    ax.annotate('', xy=(b_center, b3_y + 0.48), xytext=(b_center, b2_y - 0.40),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)

    # Row 4 & 5: Actuator Driver & Signaling Driver
    b45_y = 3.65
    b4_w = 2.35
    b5_w = 2.35
    b4_x = b_left  # 3.25
    b5_x = b_right - b5_w  # 5.90
    b4_center = b4_x + b4_w / 2.0  # 4.425
    b5_center = b5_x + b5_w / 2.0  # 7.075

    # Block 4: Actuator Driver (Left)
    b4 = FancyBboxPatch((b4_x, b45_y - 0.50), b4_w, 1.00,
                        boxstyle="round,pad=0.06,rounding_size=0.15",
                        facecolor=c_box_fill, edgecolor=c_box_border, lw=1.6, zorder=5)
    ax.add_patch(b4)
    draw_badge(b4_x + 0.28, b45_y + 0.22, 4)
    ax.text(b4_center + 0.12, b45_y + 0.22, 'Actuator Driver', fontsize=9.2, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)
    ax.text(b4_center, b45_y - 0.20, '(Relay pump;\nServo valve PWM)', fontsize=8.0, ha='center', va='center', color=c_text_muted, multialignment='center', zorder=10)

    # Block 5: Signaling Driver (Right)
    b5 = FancyBboxPatch((b5_x, b45_y - 0.50), b5_w, 1.00,
                        boxstyle="round,pad=0.06,rounding_size=0.15",
                        facecolor=c_box_fill, edgecolor=c_box_border, lw=1.6, zorder=5)
    ax.add_patch(b5)
    draw_badge(b5_x + 0.28, b45_y + 0.22, 5)
    ax.text(b5_center + 0.12, b45_y + 0.22, 'Signaling Driver', fontsize=9.2, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)
    ax.text(b5_center, b45_y - 0.20, '(3 LEDs;\nActive Buzzer)', fontsize=8.0, ha='center', va='center', color=c_text_muted, multialignment='center', zorder=10)

    # Arrows 3 -> 4 & 5
    ax.plot([b_center, b_center], [b3_y - 0.48, b45_y + 0.72], color=c_arrow, lw=1.6, zorder=4)
    ax.plot([b4_center, b5_center], [b45_y + 0.72, b45_y + 0.72], color=c_arrow, lw=1.6, zorder=4)
    ax.annotate('', xy=(b4_center, b45_y + 0.50), xytext=(b4_center, b45_y + 0.72),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)
    ax.annotate('', xy=(b5_center, b45_y + 0.50), xytext=(b5_center, b45_y + 0.72),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)

    # Block 6: HTTP REST API Handler
    b6_y = 2.15
    b6 = FancyBboxPatch((b_left, b6_y - 0.40), b_width, 0.80,
                        boxstyle="round,pad=0.06,rounding_size=0.15",
                        facecolor=c_box_fill, edgecolor=c_box_border, lw=1.6, zorder=5)
    ax.add_patch(b6)
    draw_badge(b_left + 0.35, b6_y, 6)
    ax.text(b_center + 0.15, b6_y + 0.14, 'HTTP REST API Handler', fontsize=10.5, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)
    ax.text(b_center + 0.15, b6_y - 0.16, '(Web Dashboard; JSON endpoints)', fontsize=8.2, ha='center', va='center', color=c_text_muted, zorder=10)

    # Arrows 4 & 5 -> 6
    ax.plot([b4_center, b4_center], [b45_y - 0.50, b6_y + 0.62], color=c_arrow, lw=1.6, zorder=4)
    ax.plot([b5_center, b5_center], [b45_y - 0.50, b6_y + 0.62], color=c_arrow, lw=1.6, zorder=4)
    ax.plot([b4_center, b5_center], [b6_y + 0.62, b6_y + 0.62], color=c_arrow, lw=1.6, zorder=4)
    ax.annotate('', xy=(b_center, b6_y + 0.40), xytext=(b_center, b6_y + 0.62),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)

    # External Box on Right: Web Dashboard / Wi-Fi SoftAP
    web_x = 10.05
    web_w = 1.65
    web_box = FancyBboxPatch((web_x, b6_y - 0.42), web_w, 0.84,
                             boxstyle="round,pad=0.06,rounding_size=0.15",
                             facecolor=c_box_fill, edgecolor=c_box_border, lw=1.6, zorder=5)
    ax.add_patch(web_box)
    ax.text(web_x + web_w / 2.0, b6_y, 'Web Dashboard /\nWi-Fi SoftAP', fontsize=8.2, fontweight='bold',
            ha='center', va='center', color=c_text_dark, multialignment='center', zorder=10)

    # Bidirectional arrow between Block 6 and Web Dashboard
    ax.annotate('', xy=(web_x, b6_y), xytext=(b_right, b6_y),
                arrowprops=dict(arrowstyle="<|-|>", color=c_arrow, lw=1.8, mutation_scale=13), zorder=6)
    ax.text((cont_right + web_x) / 2.0, b6_y + 0.16, 'HTTP / JSON', fontsize=8.0, fontweight='bold',
            ha='center', va='bottom', color='#374151', zorder=10)

    # Block 7: Failsafe + Watchdog
    b7_y = 0.95
    b7 = FancyBboxPatch((b_left, b7_y - 0.40), b_width, 0.80,
                        boxstyle="round,pad=0.06,rounding_size=0.15",
                        facecolor=c_box_fill, edgecolor=c_box_border, lw=1.6, zorder=5)
    ax.add_patch(b7)
    draw_badge(b_left + 0.35, b7_y, 7)
    ax.text(b_center + 0.15, b7_y + 0.14, 'Failsafe + Watchdog', fontsize=10.5, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)
    ax.text(b_center + 0.15, b7_y - 0.16, '(Heartbeat 30 s; safe AUTO fallback)', fontsize=8.2, ha='center', va='center', color=c_text_muted, zorder=10)

    # Arrow 6 -> 7
    ax.annotate('', xy=(b_center, b7_y + 0.40), xytext=(b_center, b6_y - 0.40),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)

    # Feedback Dashed Arrow from Block 7 to Block 3 (runs cleanly along left margin, avoiding Block 4)
    feedback_x = 2.75
    ax.plot([b_left, feedback_x], [b7_y, b7_y], color='#4b5563', ls='--', lw=1.6, zorder=6)
    ax.plot([feedback_x, feedback_x], [b7_y, b3_y], color='#4b5563', ls='--', lw=1.6, zorder=6)
    ax.annotate('', xy=(b_left, b3_y), xytext=(feedback_x, b3_y),
                arrowprops=dict(arrowstyle="-|>", color='#4b5563', ls='--', lw=1.6, mutation_scale=12), zorder=6)
    ax.text(2.52, (b7_y + b3_y) / 2.0, 'AUTO Fallback (30s timeout)', fontsize=7.2, color='#4b5563',
            ha='center', va='center', rotation=90, zorder=10)

    plt.tight_layout()
    for p in output_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        plt.savefig(p, dpi=300, bbox_inches='tight', facecolor='#ffffff')
    plt.close()
    print("Firmware modules diagram saved successfully.")


def create_main_loop_flowchart(output_paths):
    fig, ax = plt.subplots(figsize=(7.6, 10.2), dpi=300)
    ax.set_xlim(0, 10.6)
    ax.set_ylim(0, 14.2)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Monochrome Palette
    c_box_fill = '#f3f4f6'
    c_box_border = '#111827'
    c_decision_fill = '#e5e7eb'
    c_decision_border = '#111827'
    c_arrow = '#000000'
    c_text_dark = '#000000'

    # 1. Start Pill
    start_y = 13.5
    start_box = FancyBboxPatch((3.8, start_y - 0.28), 2.4, 0.56,
                               boxstyle="round,pad=0.06,rounding_size=0.28",
                               facecolor=c_box_fill, edgecolor=c_box_border, lw=1.8, zorder=5)
    ax.add_patch(start_box)
    ax.text(5.0, start_y, 'Start', fontsize=11.5, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)

    # Arrow Start -> setup()
    ax.annotate('', xy=(5.0, 12.65), xytext=(5.0, start_y - 0.28),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)

    # 2. setup() Box
    setup_y = 11.60
    setup_box = FancyBboxPatch((1.6, setup_y - 1.00), 6.8, 2.05,
                               boxstyle="round,pad=0.06,rounding_size=0.15",
                               facecolor=c_box_fill, edgecolor=c_box_border, lw=1.8, zorder=5)
    ax.add_patch(setup_box)
    setup_text = (
        "setup(): Serial 115200; configure GPIO;\n"
        "Relay INPUT (High-Z); Servo 0 deg;\n"
        "start Wi-Fi SoftAP + mDNS; register API routes;\n"
        "server.begin()"
    )
    ax.text(5.0, setup_y + 0.05, setup_text, fontsize=9.0, ha='center', va='center',
            color=c_text_dark, multialignment='center', linespacing=1.35, zorder=10)

    # Arrow setup() -> Enter loop()
    ax.annotate('', xy=(5.0, 10.05), xytext=(5.0, setup_y - 1.00),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)

    # 3. Enter loop() Box
    enter_y = 9.75
    enter_box = FancyBboxPatch((3.7, enter_y - 0.26), 2.6, 0.52,
                               boxstyle="round,pad=0.06,rounding_size=0.15",
                               facecolor=c_box_fill, edgecolor=c_box_border, lw=1.8, zorder=5)
    ax.add_patch(enter_box)
    ax.text(5.0, enter_y, 'Enter loop()', fontsize=10.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)

    # Arrow Enter loop() -> server.handleClient()
    ax.annotate('', xy=(5.0, 8.85), xytext=(5.0, enter_y - 0.26),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)

    # 4. server.handleClient() Box
    handle_y = 8.55
    handle_box = FancyBboxPatch((3.0, handle_y - 0.28), 4.0, 0.56,
                                boxstyle="round,pad=0.06,rounding_size=0.15",
                                facecolor=c_box_fill, edgecolor=c_box_border, lw=1.8, zorder=5)
    ax.add_patch(handle_box)
    ax.text(5.0, handle_y, 'server.handleClient()', fontsize=10.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)

    # Arrow handleClient -> Decision 1
    ax.annotate('', xy=(5.0, 7.55), xytext=(5.0, handle_y - 0.28),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)

    # 5. Decision 1 (Diamond): millis() - lastSensorRead >= 150 ms?
    d1_y = 6.85
    d1_pts = [[5.0, d1_y + 0.68], [7.1, d1_y], [5.0, d1_y - 0.68], [2.9, d1_y]]
    d1 = Polygon(d1_pts, closed=True, facecolor=c_decision_fill, edgecolor=c_decision_border, lw=1.8, zorder=5)
    ax.add_patch(d1)
    ax.text(5.0, d1_y, 'millis() - lastSensorRead\n>= 150 ms?', fontsize=8.8, fontweight='bold',
            ha='center', va='center', color=c_text_dark, multialignment='center', zorder=10)

    # Branch YES of Decision 1: Arrow right to updateSensors()
    r_center = 8.75
    up_x = 7.60
    up_w = 2.30
    ax.annotate('', xy=(up_x, d1_y), xytext=(7.1, d1_y),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)
    ax.text(7.35, d1_y + 0.22, 'Yes', fontsize=9.2, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)

    # updateSensors() box
    up_y = d1_y
    up_box = FancyBboxPatch((up_x, up_y - 0.28), up_w, 0.56,
                            boxstyle="round,pad=0.06,rounding_size=0.15",
                            facecolor=c_box_fill, edgecolor=c_box_border, lw=1.6, zorder=5)
    ax.add_patch(up_box)
    ax.text(r_center, up_y, 'updateSensors()', fontsize=8.8, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)

    # Arrow updateSensors() down to evaluateSystemStateAuto()
    eval_y = 5.70
    ax.annotate('', xy=(r_center, eval_y + 0.30), xytext=(r_center, up_y - 0.28),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)

    # evaluateSystemStateAuto() box
    eval_w = 2.55
    eval_x = r_center - eval_w / 2.0  # 7.475 -> ends at 10.025, fits well inside 10.6
    eval_box = FancyBboxPatch((eval_x, eval_y - 0.30), eval_w, 0.60,
                             boxstyle="round,pad=0.06,rounding_size=0.15",
                             facecolor=c_box_fill, edgecolor=c_box_border, lw=1.6, zorder=5)
    ax.add_patch(eval_box)
    ax.text(r_center, eval_y, 'evaluateSystemStateAuto()', fontsize=7.8, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)

    # Merge line from evaluateSystemStateAuto() back to main trunk
    ax.plot([r_center, r_center], [eval_y - 0.30, 4.90], color=c_arrow, lw=1.6, zorder=4)
    ax.plot([r_center, 5.0], [4.90, 4.90], color=c_arrow, lw=1.6, zorder=4)

    # Branch NO of Decision 1: Goes straight down
    ax.plot([5.0, 5.0], [d1_y - 0.68, 4.90], color=c_arrow, lw=1.6, zorder=4)
    ax.text(4.75, d1_y - 0.90, 'No', fontsize=9.2, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)

    # Arrow from merge point into applyOutputs()
    ax.annotate('', xy=(5.0, 4.50), xytext=(5.0, 4.90),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)

    # 6. applyOutputs() Box
    app_y = 4.22
    app_box = FancyBboxPatch((3.1, app_y - 0.28), 3.8, 0.56,
                             boxstyle="round,pad=0.06,rounding_size=0.15",
                             facecolor=c_box_fill, edgecolor=c_box_border, lw=1.8, zorder=5)
    ax.add_patch(app_box)
    ax.text(5.0, app_y, 'applyOutputs()', fontsize=10.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)

    # Arrow applyOutputs() -> Decision 2
    ax.annotate('', xy=(5.0, 3.25), xytext=(5.0, app_y - 0.28),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)

    # 7. Decision 2 (Diamond): MANUAL heartbeat timeout > 30 s?
    d2_y = 2.55
    d2_pts = [[5.0, d2_y + 0.68], [7.1, d2_y], [5.0, d2_y - 0.68], [2.9, d2_y]]
    d2 = Polygon(d2_pts, closed=True, facecolor=c_decision_fill, edgecolor=c_decision_border, lw=1.8, zorder=5)
    ax.add_patch(d2)
    ax.text(5.0, d2_y, 'MANUAL heartbeat\ntimeout > 30 s?', fontsize=8.8, fontweight='bold',
            ha='center', va='center', color=c_text_dark, multialignment='center', zorder=10)

    # Branch YES of Decision 2: Arrow right to Switch to AUTO
    sw_x = 7.60
    sw_w = 2.30
    ax.annotate('', xy=(sw_x, d2_y), xytext=(7.1, d2_y),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)
    ax.text(7.35, d2_y + 0.22, 'Yes', fontsize=9.2, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)

    # Switch to AUTO box
    sw_y = d2_y
    sw_box = FancyBboxPatch((sw_x, sw_y - 0.28), sw_w, 0.56,
                            boxstyle="round,pad=0.06,rounding_size=0.15",
                            facecolor=c_box_fill, edgecolor=c_box_border, lw=1.6, zorder=5)
    ax.add_patch(sw_box)
    ax.text(r_center, sw_y, 'Switch to AUTO', fontsize=8.8, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)

    # Merge line from Switch to AUTO back to main trunk
    ax.plot([r_center, r_center], [sw_y - 0.28, 1.45], color=c_arrow, lw=1.6, zorder=4)
    ax.plot([r_center, 5.0], [1.45, 1.45], color=c_arrow, lw=1.6, zorder=4)

    # Branch NO of Decision 2: Goes straight down
    ax.plot([5.0, 5.0], [d2_y - 0.68, 1.45], color=c_arrow, lw=1.6, zorder=4)
    ax.text(4.75, d2_y - 0.90, 'No', fontsize=9.2, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)

    # Arrow from merge point into Reset Task Watchdog
    ax.annotate('', xy=(5.0, 1.05), xytext=(5.0, 1.45),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)

    # 8. Reset Task Watchdog Box
    wdt_y = 0.78
    wdt_box = FancyBboxPatch((3.0, wdt_y - 0.28), 4.0, 0.56,
                             boxstyle="round,pad=0.06,rounding_size=0.15",
                             facecolor=c_box_fill, edgecolor=c_box_border, lw=1.8, zorder=5)
    ax.add_patch(wdt_box)
    ax.text(5.0, wdt_y, 'Reset Task Watchdog', fontsize=10.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)

    # 9. Main Feedback Loop Arrow
    ax.plot([3.0, 0.8], [wdt_y, wdt_y], color=c_arrow, lw=1.8, zorder=4)
    ax.plot([0.8, 0.8], [wdt_y, handle_y], color=c_arrow, lw=1.8, zorder=4)
    ax.annotate('', xy=(3.0, handle_y), xytext=(0.8, handle_y),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.8, mutation_scale=14), zorder=4)

    # Branch NO of Decision 2: Goes straight down
    ax.plot([5.0, 5.0], [d2_y - 0.68, 1.45], color=c_arrow, lw=1.6, zorder=4)
    ax.text(4.75, d2_y - 0.90, 'No', fontsize=9.2, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)

    # Arrow from merge point into Reset Task Watchdog
    ax.annotate('', xy=(5.0, 1.05), xytext=(5.0, 1.45),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.6, mutation_scale=12), zorder=4)

    # 8. Reset Task Watchdog Box
    wdt_y = 0.78
    wdt_box = FancyBboxPatch((3.0, wdt_y - 0.28), 4.0, 0.56,
                             boxstyle="round,pad=0.06,rounding_size=0.15",
                             facecolor=c_box_fill, edgecolor=c_box_border, lw=1.8, zorder=5)
    ax.add_patch(wdt_box)
    ax.text(5.0, wdt_y, 'Reset Task Watchdog', fontsize=10.0, fontweight='bold', ha='center', va='center', color=c_text_dark, zorder=10)

    # 9. Main Feedback Loop Arrow
    ax.plot([3.0, 0.8], [wdt_y, wdt_y], color=c_arrow, lw=1.8, zorder=4)
    ax.plot([0.8, 0.8], [wdt_y, handle_y], color=c_arrow, lw=1.8, zorder=4)
    ax.annotate('', xy=(3.0, handle_y), xytext=(0.8, handle_y),
                arrowprops=dict(arrowstyle="-|>", color=c_arrow, lw=1.8, mutation_scale=14), zorder=4)

    plt.tight_layout()
    for p in output_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        plt.savefig(p, dpi=300, bbox_inches='tight', facecolor='#ffffff')
    plt.close()
    print("Main loop flowchart saved successfully.")

if __name__ == '__main__':
    firmware_paths = [
        os.path.join('figures', 'firmware_modules_diagram.png'),
        os.path.join('report', 'figures', 'firmware_modules_diagram.png')
    ]
    flowchart_paths = [
        os.path.join('figures', 'main_loop_flowchart.png'),
        os.path.join('report', 'figures', 'main_loop_flowchart.png')
    ]
    create_firmware_modules_diagram(firmware_paths)
    create_main_loop_flowchart(flowchart_paths)
