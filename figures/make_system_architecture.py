import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def make_architecture_diagram_bw():
    # Canvas setup: 15.0 x 8.8 inches, 300 DPI, Pure Monochrome (Black & White)
    # Tích hợp đúng 5 khối chức năng theo Mục 2.1 (đã loại bỏ khối nguồn)
    fig, ax = plt.subplots(figsize=(15.0, 8.8), dpi=300)
    ax.set_xlim(0, 15.0)
    ax.set_ylim(0, 8.8)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Main Header
    ax.text(7.5, 8.42, 'SƠ ĐỒ TỔNG QUAN KIẾN TRÚC HỆ THỐNG TRẠM FLOODGUARD', 
            fontsize=13.5, fontweight='bold', ha='center', va='center', color='#000000')
    ax.text(7.5, 8.14, 'Tích hợp 5 khối chức năng: Cảm biến, Xử lý trung tâm, Chấp hành, Cảnh báo và Giám sát Web', 
            fontsize=9.2, style='italic', ha='center', va='center', color='#333333')

    # Styling helper for black & white cards
    def draw_card(x, y, w, h, title, desc=None, bold_title=True, fontsize_title=8.2, fontsize_desc=7.3):
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.0,rounding_size=0.08',
                                     linewidth=1.0, edgecolor='#000000', facecolor='#ffffff', zorder=2)
        ax.add_patch(box)
        if desc:
            ax.text(x + w/2, y + h*0.70, title, fontsize=fontsize_title, fontweight='bold' if bold_title else 'normal',
                    ha='center', va='center', color='#000000', zorder=3)
            ax.text(x + w/2, y + h*0.30, desc, fontsize=fontsize_desc, ha='center', va='center', color='#222222', zorder=3)
        else:
            ax.text(x + w/2, y + h/2, title, fontsize=fontsize_title, fontweight='bold' if bold_title else 'normal',
                    ha='center', va='center', color='#000000', zorder=3)

    label_bbox = dict(boxstyle='square,pad=0.2', facecolor='#ffffff', edgecolor='#666666', lw=0.6, alpha=1.0)

    # =========================================================================
    # 1. KHỐI 5: MÁY TÍNH VẬN HÀNH & GIÁM SÁT TỪ XA (TOP)
    # =========================================================================
    # x=4.6 to 10.4 (width 5.8), y=6.45 to 7.75 (height 1.30)
    box_web = patches.FancyBboxPatch((4.6, 6.45), 5.8, 1.30, boxstyle='round,pad=0.0,rounding_size=0.12',
                                     linewidth=1.4, edgecolor='#000000', facecolor='#ffffff', zorder=2)
    ax.add_patch(box_web)
    ax.text(7.5, 7.52, 'KHỐI 5: MÁY TÍNH VẬN HÀNH & GIÁM SÁT TỪ XA', 
            fontsize=9.5, fontweight='bold', ha='center', va='center', color='#000000', zorder=4)

    draw_card(4.8, 6.60, 2.5, 0.72, 'Giao Diện Web Dashboard', 'Giám sát Telemetry & Can thiệp từ xa')
    draw_card(7.7, 6.60, 2.5, 0.72, 'Máy Tính Kỹ Thuật', 'Nạp firmware PlatformIO & Serial Debug')

    # =========================================================================
    # 2. KHỐI 1: KHỐI XỬ LÝ TRUNG TÂM (ESP32 SoC - CENTER)
    # =========================================================================
    # x=4.6 to 10.4 (width 5.8), y=0.50 to 5.80 (height 5.30)
    box_esp = patches.FancyBboxPatch((4.6, 0.50), 5.8, 5.30, boxstyle='round,pad=0.0,rounding_size=0.15',
                                     linewidth=1.6, edgecolor='#000000', facecolor='#ffffff', zorder=2)
    ax.add_patch(box_esp)
    ax.text(7.5, 5.55, 'KHỐI 1: XỬ LÝ TRUNG TÂM (CENTRAL PROCESSING CORE)', 
            fontsize=9.8, fontweight='bold', ha='center', va='center', color='#000000', zorder=4)
    ax.text(7.5, 5.32, 'Vi Điều Khiển ESP32 DevKit V1 (Xtensa 32-bit Dual-Core 240MHz)', 
            fontsize=8.0, style='italic', ha='center', va='center', color='#333333', zorder=4)

    # 4 Module chức năng nhúng bên trong ESP32
    modules = [
        ('1. Khối Trích Mẫu & Lọc Nhiễu Cảm Biến', 
         'Đo xung siêu âm ToF (chu kỳ 150ms), lọc trung vị Median-of-3, đọc mưa DO/AO', 4.25),
        ('2. Thuật Toán Điều Khiển FSM & Dải Trễ (Hysteresis)', 
         'Quản lý 4 trạng thái (NORMAL/WARNING/DANGER/CRITICAL), chống rung Debounce', 3.20),
        ('3. Khối Quản Lý Cơ Cấu Chấp Hành & An Toàn', 
         'Điều khiển Relay bơm (Min-run 5s), Servo van xả (Slew-rate), bảo vệ khi MANUAL', 2.15),
        ('4. Máy Chủ Web Server Nhúng & Failsafe Watchdog', 
         'REST API điều khiển, Failsafe Watchdog tự về AUTO khi mất kết nối > 30s', 1.10)
    ]

    for title, desc, y_pos in modules:
        m_box = patches.FancyBboxPatch((4.8, y_pos), 5.4, 0.88, boxstyle='round,pad=0.0,rounding_size=0.06',
                                       linewidth=1.0, edgecolor='#000000', facecolor='#fbfbfb', zorder=3)
        ax.add_patch(m_box)
        ax.text(7.5, y_pos + 0.58, title, fontsize=8.2, fontweight='bold', ha='center', va='center', color='#000000', zorder=4)
        ax.text(7.5, y_pos + 0.28, desc, fontsize=7.4, ha='center', va='center', color='#222222', zorder=4)

    ax.text(7.5, 0.76, 'Hệ điều hành FreeRTOS nhúng  •  Bộ nhớ 520KB SRAM  •  Tích hợp Wi-Fi 802.11 b/g/n', 
            fontsize=7.2, style='italic', ha='center', va='center', color='#444444', zorder=4)

    # =========================================================================
    # 3. KHỐI 2: CẢM BIẾN ĐẦU VÀO (SENSORS - LEFT)
    # =========================================================================
    # x=0.7 to 3.5 (width 2.8), y=0.50 to 5.80 (height 5.30) - Khớp cạnh đáy với Khối 1
    box_sens = patches.FancyBboxPatch((0.7, 0.50), 2.8, 5.30, boxstyle='round,pad=0.0,rounding_size=0.12',
                                      linewidth=1.4, edgecolor='#000000', facecolor='#ffffff', zorder=2)
    ax.add_patch(box_sens)
    ax.text(2.1, 5.55, 'KHỐI 2: CẢM BIẾN (SENSORS)', 
            fontsize=9.5, fontweight='bold', ha='center', va='center', color='#000000', zorder=4)

    # Sub-card 2.1: HC-SR04
    card_us = patches.FancyBboxPatch((0.9, 3.25), 2.4, 1.95, boxstyle='round,pad=0.0,rounding_size=0.08',
                                     linewidth=1.0, edgecolor='#000000', facecolor='#ffffff', zorder=3)
    ax.add_patch(card_us)
    ax.text(2.1, 4.85, 'Cảm Biến Siêu Âm HC-SR04', fontsize=8.4, fontweight='bold', ha='center', va='center', color='#000000', zorder=4)
    ax.text(2.1, 4.05, '• Đo khoảng cách mặt nước hồ\n• Dải làm việc: 2.0 - 10.0 cm\n• Xung Trig (Out) & Echo (In)', 
            fontsize=7.4, ha='center', va='center', color='#222222', zorder=4)

    # Sub-card 2.2: FC-37
    card_rn = patches.FancyBboxPatch((0.9, 0.85), 2.4, 1.95, boxstyle='round,pad=0.0,rounding_size=0.08',
                                     linewidth=1.0, edgecolor='#000000', facecolor='#ffffff', zorder=3)
    ax.add_patch(card_rn)
    ax.text(2.1, 2.45, 'Cảm Biến Mưa FC-37 & LM393', fontsize=8.4, fontweight='bold', ha='center', va='center', color='#000000', zorder=4)
    ax.text(2.1, 1.65, '• Phát hiện nước bề mặt & đo mưa\n• Ngõ ra số DO (GPIO 34)\n• Ngõ ra tương tự AO (GPIO 35)', 
            fontsize=7.4, ha='center', va='center', color='#222222', zorder=4)

    # =========================================================================
    # 4. KHỐI 3: CƠ CẤU CHẤP HÀNH (ACTUATORS - RIGHT TOP)
    # =========================================================================
    # x=11.5 to 14.3 (width 2.8), y=3.20 to 5.80 (height 2.60)
    box_act = patches.FancyBboxPatch((11.5, 3.20), 2.8, 2.60, boxstyle='round,pad=0.0,rounding_size=0.12',
                                     linewidth=1.4, edgecolor='#000000', facecolor='#ffffff', zorder=2)
    ax.add_patch(box_act)
    ax.text(12.9, 5.55, 'KHỐI 3: CHẤP HÀNH (ACTUATORS)', 
            fontsize=9.5, fontweight='bold', ha='center', va='center', color='#000000', zorder=4)

    draw_card(11.7, 4.40, 2.4, 0.88, 'Module Relay 5V & Bơm Mini', 'Bơm xả cạn cưỡng bức chống tràn', fontsize_title=8.2, fontsize_desc=7.3)
    draw_card(11.7, 3.38, 2.4, 0.88, 'Động Cơ Servo SG90 & Van Xả', 'Điều tiết 3 góc: 0° - 90° - 180°', fontsize_title=8.2, fontsize_desc=7.3)

    # =========================================================================
    # 5. KHỐI 4: CẢNH BÁO TẠI CHỖ (SIGNALING - RIGHT BOTTOM)
    # =========================================================================
    # x=11.5 to 14.3 (width 2.8), y=0.50 to 3.10 (height 2.60) - Khớp cạnh đáy với Khối 1
    box_sig = patches.FancyBboxPatch((11.5, 0.50), 2.8, 2.60, boxstyle='round,pad=0.0,rounding_size=0.12',
                                     linewidth=1.4, edgecolor='#000000', facecolor='#ffffff', zorder=2)
    ax.add_patch(box_sig)
    ax.text(12.9, 2.85, 'KHỐI 4: CẢNH BÁO TẠI CHỖ', 
            fontsize=9.5, fontweight='bold', ha='center', va='center', color='#000000', zorder=4)

    draw_card(11.7, 1.70, 2.4, 0.88, 'Cụm 3 Đèn LED Màu Báo Mức', 'Xanh (An toàn), Vàng (Cảnh báo), Đỏ (Nguy)', fontsize_title=8.0, fontsize_desc=7.1)
    draw_card(11.7, 0.68, 2.4, 0.88, 'Còi Báo Động Active Buzzer 5V', 'Phát âm thanh cảnh báo theo cấp', fontsize_title=8.2, fontsize_desc=7.3)

    # =========================================================================
    # 6. MŨI TÊN KẾT NỐI (ARROWS & LABELS)
    # =========================================================================
    arrow_kw = dict(arrowstyle='-|>', lw=1.3, color='#000000', zorder=5, mutation_scale=12)
    arrow_bi = dict(arrowstyle='<|-|>', lw=1.4, color='#000000', zorder=5, mutation_scale=13)

    # Sensors -> ESP32 (from x=3.5 to x=4.6, gap = 1.1)
    # HC-SR04
    ax.annotate('', xy=(4.6, 4.22), xytext=(3.5, 4.22), arrowprops=arrow_kw)
    ax.text(4.05, 4.22, 'Trig, Echo\n(D13, D12)', fontsize=7.2, fontweight='bold', ha='center', va='center', 
            color='#000000', bbox=label_bbox, zorder=6)

    # FC-37
    ax.annotate('', xy=(4.6, 1.82), xytext=(3.5, 1.82), arrowprops=arrow_kw)
    ax.text(4.05, 1.82, 'DO, AO\n(D34, D35)', fontsize=7.2, fontweight='bold', ha='center', va='center', 
            color='#000000', bbox=label_bbox, zorder=6)

    # ESP32 -> Actuators (from x=10.4 to x=11.5, gap = 1.1)
    # Relay
    ax.annotate('', xy=(11.5, 4.84), xytext=(10.4, 4.84), arrowprops=arrow_kw)
    ax.text(10.95, 4.84, 'Relay\n(GPIO 23)', fontsize=7.2, fontweight='bold', ha='center', va='center', 
            color='#000000', bbox=label_bbox, zorder=6)

    # Servo
    ax.annotate('', xy=(11.5, 3.82), xytext=(10.4, 3.82), arrowprops=arrow_kw)
    ax.text(10.95, 3.82, 'PWM 50Hz\n(GPIO 27)', fontsize=7.2, fontweight='bold', ha='center', va='center', 
            color='#000000', bbox=label_bbox, zorder=6)

    # ESP32 -> Signaling (from x=10.4 to x=11.5, gap = 1.1)
    # LEDs
    ax.annotate('', xy=(11.5, 2.14), xytext=(10.4, 2.14), arrowprops=arrow_kw)
    ax.text(10.95, 2.14, '3x LEDs\n(D21,19,18)', fontsize=7.2, fontweight='bold', ha='center', va='center', 
            color='#000000', bbox=label_bbox, zorder=6)

    # Buzzer
    ax.annotate('', xy=(11.5, 1.12), xytext=(10.4, 1.12), arrowprops=arrow_kw)
    ax.text(10.95, 1.12, 'Buzzer\n(GPIO 4)', fontsize=7.2, fontweight='bold', ha='center', va='center', 
            color='#000000', bbox=label_bbox, zorder=6)

    # ESP32 <-> Operator Station (Vertical arrows between y=5.80 and y=6.45, gap = 0.65)
    # Wi-Fi link
    ax.annotate('', xy=(5.85, 6.45), xytext=(5.85, 5.80), arrowprops=arrow_bi)
    ax.text(5.65, 6.12, 'Wi-Fi SoftAP\n(192.168.4.1)', fontsize=7.2, fontweight='bold', ha='right', va='center', 
            color='#000000', bbox=label_bbox, zorder=6)

    # UART link
    ax.annotate('', xy=(9.15, 6.45), xytext=(9.15, 5.80), arrowprops=arrow_bi)
    ax.text(9.35, 6.12, 'Micro-USB\n(UART COM5)', fontsize=7.2, fontweight='bold', ha='left', va='center', 
            color='#000000', bbox=label_bbox, zorder=6)

    # Output save to official figures and report directories
    out_paths = [
        os.path.join("figures", "system_architecture.png"),
        os.path.join("report", "figures", "system_architecture.png"),
        os.path.join("figures", "test_system_architecture.png")
    ]
    plt.tight_layout()
    for p in out_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        plt.savefig(p, dpi=300, bbox_inches='tight')
        print(f"Generated diagram at: {p}")
    plt.close(fig)

if __name__ == '__main__':
    make_architecture_diagram_bw()
