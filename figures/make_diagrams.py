import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

out_dirs = [
    os.path.join("d:\\1. project\\FloodGuard", "figures"),
    os.path.join("d:\\1. project\\FloodGuard", "report", "figures")
]
for d in out_dirs:
    os.makedirs(d, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 1.0

def save_fig(fig, filename):
    plt.tight_layout()
    for d in out_dirs:
        fig.savefig(os.path.join(d, filename), dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Generated: {filename}")

# -------------------------------------------------------------
# 1. OVERALL SYSTEM USE CASE DIAGRAM
# -------------------------------------------------------------
def make_uc_overall():
    fig, ax = plt.subplots(figsize=(15, 11), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 11)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    ax.text(7.5, 10.5, "SƠ ĐỒ TỔNG THỂ USE CASE HỆ THỐNG FLOODGUARD", 
            fontsize=16, fontweight='bold', ha='center', color='#0f172a')
    ax.text(7.5, 10.15, "Phân định rõ ranh giới hệ thống, Tác nhân Môi trường, Ngoại vi và Con người", 
            fontsize=10.5, style='italic', ha='center', color='#475569')

    # System Boundary Box
    sys_box = FancyBboxPatch((3.8, 0.6), 7.4, 9.2, boxstyle="round,pad=0.2,rounding_size=0.3",
                             facecolor='#f8fafc', edgecolor='#0284c7', linewidth=2.5)
    ax.add_patch(sys_box)
    ax.text(7.5, 9.55, "Ranh giới Hệ Thống: Trạm Điều Khiển Trung Tâm FloodGuard (ESP32 Firmware)", 
            fontsize=11.5, fontweight='bold', ha='center', color='#0369a1',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#e0f2fe', edgecolor='#38bdf8', lw=1.2))

    use_cases = [
        ("UC01: Đọc & Tiền Xử Lý\nDữ Liệu Cảm Biến", 5.6, 8.6, '#38bdf8'),
        ("UC02: Đánh Giá Trạng Thái FSM\n& Xử Lý Dải Trễ (Hysteresis)", 9.4, 8.6, '#38bdf8'),
        ("UC03: Tự Động Điều Khiển\nMáy Bơm Thoát Nước", 5.6, 7.1, '#3b82f6'),
        ("UC04: Tự Động Điều Khiển\nVan Thoát Lũ (Servo SG90)", 9.4, 7.1, '#3b82f6'),
        ("UC05: Tự Động Báo Động\nTại Chỗ (LED & Buzzer)", 7.5, 5.7, '#f59e0b'),
        ("UC06: Tự Động Chuyển An Toàn\n(Failsafe to AUTO Mode)", 7.5, 4.4, '#ef4444'),
        ("UC07: Truyền Nhận Dữ Liệu\nThời Gian Thực (API / Telemetry)", 7.5, 3.1, '#10b981'),
        ("UC08: Giám Sát Trạng Thái\nTừ Xa (Web Dashboard)", 5.6, 1.8, '#8b5cf6'),
        ("UC09: Chuyển Đổi Chế Độ\n(AUTO / MANUAL)", 9.4, 1.8, '#8b5cf6'),
        ("UC10: Can Thiệp Cưỡng Chế\nThiết Bị Từ Web", 7.5, 1.0, '#ec4899')
    ]

    for uc_text, x, y, col in use_cases:
        ellipse = patches.Ellipse((x, y), 3.2, 0.85, facecolor='#ffffff', 
                                  edgecolor=col, linewidth=2, zorder=3)
        ax.add_patch(ellipse)
        ax.text(x, y, uc_text, fontsize=8.5, fontweight='bold', ha='center', va='center', 
                color='#1e293b', zorder=4)

    def draw_actor(x, y, name, role_type, icon_color='#2563eb'):
        circle = plt.Circle((x, y + 0.35), 0.22, facecolor='#ffffff', edgecolor=icon_color, lw=2, zorder=5)
        ax.add_patch(circle)
        ax.plot([x, x], [y + 0.13, y - 0.28], color=icon_color, lw=2.2, zorder=5)
        ax.plot([x - 0.25, x + 0.25], [y, y], color=icon_color, lw=2.2, zorder=5)
        ax.plot([x, x - 0.22], [y - 0.28, y - 0.58], color=icon_color, lw=2.2, zorder=5)
        ax.plot([x, x + 0.22], [y - 0.28, y - 0.58], color=icon_color, lw=2.2, zorder=5)
        ax.text(x, y - 0.82, name, fontsize=9.5, fontweight='bold', ha='center', va='top', color='#0f172a')
        ax.text(x, y - 1.05, f"«{role_type}»", fontsize=7.5, style='italic', ha='center', va='top', color='#64748b')

    draw_actor(1.8, 8.8, "Môi Trường\nNước Lũ & Mưa", "Tác nhân Môi trường", '#0284c7')
    draw_actor(1.8, 6.7, "Khối Cảm Biến\n(HC-SR04 & Mưa)", "Ngoại vi Đầu vào", '#0369a1')
    draw_actor(13.2, 7.0, "Khối Chấp Hành\n(Bơm, Van, LED, Còi)", "Ngoại vi Đầu ra", '#b45309')
    draw_actor(13.2, 2.3, "Người Vận Hành\n(Giám Sát Viên)", "Tác nhân Con người", '#6d28d9')
    draw_actor(1.8, 3.1, "Hạ Tầng Wi-Fi\n& Client Browser", "Hệ thống Mạng", '#059669')

    connections = [
        ((1.8, 8.2), (1.8, 7.5)),
        ((2.4, 6.7), (4.0, 8.6)),
        ((7.2, 8.6), (7.8, 8.6)),
        ((8.4, 8.2), (6.4, 7.5)),
        ((9.4, 8.2), (9.4, 7.5)),
        ((8.4, 8.2), (8.0, 6.1)),
        ((7.2, 7.1), (12.6, 7.3)),
        ((11.0, 7.1), (12.6, 7.1)),
        ((9.1, 5.7), (12.6, 6.7)),
        ((2.4, 3.1), (5.9, 4.4)),
        ((2.4, 3.1), (5.9, 3.1)),
        ((7.5, 2.7), (6.2, 2.2)),
        ((12.6, 2.3), (7.2, 1.8)),
        ((12.6, 2.3), (11.0, 1.8)),
        ((12.6, 2.3), (9.1, 1.0)),
        ((8.9, 1.2), (13.2, 6.0))
    ]

    for p1, p2 in connections:
        arrow = FancyArrowPatch(p1, p2, arrowstyle='->', mutation_scale=12,
                                color='#94a3b8', linewidth=1.4, linestyle='--')
        ax.add_patch(arrow)

    save_fig(fig, "uc_overall_diagram.png")

# -------------------------------------------------------------
# 2. UC01 DIAGRAM: Đọc & Tiền Xử Lý Dữ Liệu Cảm Biến
# -------------------------------------------------------------
def make_uc01():
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    ax.text(6, 6.0, "UC01: ĐỌC VÀ TIỀN XỬ LÝ DỮ LIỆU CẢM BIẾN", fontsize=14, fontweight='bold', ha='center', color='#0f172a')
    ax.text(6, 5.65, "Tác nhân Môi trường tác động vật lý -> Cảm biến thu nhận -> ESP32 lọc trung vị & quy đổi %", 
            fontsize=9.5, style='italic', ha='center', color='#475569')

    boxes = [
        ("Môi Trường Vật Lý\n(Mặt nước hồ dập dềnh,\nHạt mưa rơi trên bản cực)", 1.5, 4.0, 2.4, 1.2, '#e0f2fe', '#0284c7'),
        ("Khối Cảm Biến Ngoại Vi\nHC-SR04 (Trig/Echo)\nCảm biến mưa (AO/DO)", 4.5, 4.0, 2.5, 1.2, '#f0fdf4', '#16a34a'),
        ("Bộ Lọc Trung Vị (Median Filter)\nLấy 3 mẫu cách nhau 12ms\nLoại bỏ nhiễu gai xung EMI", 7.6, 4.0, 2.5, 1.2, '#fef3c7', '#d97706'),
        ("Quy Đổi Mực Nước %\n& Phân Tầng Cấp Mưa\n(50cm: 0% -> 5cm: 100%)", 10.6, 4.0, 2.4, 1.2, '#f3e8ff', '#9333ea')
    ]

    for text, x, y, w, h, bg, border in boxes:
        box = FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.1,rounding_size=0.15",
                             facecolor=bg, edgecolor=border, lw=1.8)
        ax.add_patch(box)
        ax.text(x, y, text, fontsize=8.5, fontweight='bold', ha='center', va='center', color='#1e293b')

    # Arrows
    ax.add_patch(FancyArrowPatch((2.7, 4.0), (3.25, 4.0), arrowstyle='->', mutation_scale=14, color='#0284c7', lw=2))
    ax.text(2.97, 4.25, "Sóng âm /\nTiếp xúc", fontsize=7.5, ha='center', color='#0369a1')

    ax.add_patch(FancyArrowPatch((5.75, 4.0), (6.35, 4.0), arrowstyle='->', mutation_scale=14, color='#16a34a', lw=2))
    ax.text(6.05, 4.25, "Xung Echo /\nADC 12-bit", fontsize=7.5, ha='center', color='#15803d')

    ax.add_patch(FancyArrowPatch((8.85, 4.0), (9.4, 4.0), arrowstyle='->', mutation_scale=14, color='#d97706', lw=2))
    ax.text(9.12, 4.25, "Khoảng cách\nsạch", fontsize=7.5, ha='center', color='#b45309')

    # Output to FSM Box below
    out_box = FancyBboxPatch((4.5, 1.2), 6.0, 1.2, boxstyle="round,pad=0.1,rounding_size=0.15",
                             facecolor='#f8fafc', edgecolor='#64748b', lw=1.5, ls='--')
    ax.add_patch(out_box)
    ax.text(7.5, 1.8, "Đầu ra chuẩn hóa cung cấp cho UC02 & UC07:", fontsize=9, fontweight='bold', ha='center', color='#334155')
    ax.text(7.5, 1.45, "• waterPercent (0 - 100%)    • currentDistance (cm)", fontsize=8.5, ha='center', color='#0f172a')
    ax.text(7.5, 1.2, "• isRaining, isHeavyRain, isSubmerged (3 cấp mưa)", fontsize=8.5, ha='center', color='#0f172a')

    ax.add_patch(FancyArrowPatch((10.6, 3.4), (10.6, 2.4), arrowstyle='->', mutation_scale=14, color='#9333ea', lw=2))

    save_fig(fig, "uc01_sensor_processing.png")

# -------------------------------------------------------------
# 3. UC02 DIAGRAM: FSM & Hysteresis
# -------------------------------------------------------------
def make_uc02():
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    ax.text(6, 7.0, "UC02: ĐÁNH GIÁ TRẠNG THÁI FSM & XỬ LÝ DẢI TRỄ (HYSTERESIS)", fontsize=14, fontweight='bold', ha='center', color='#0f172a')
    ax.text(6, 6.65, "Chống dao động bật/tắt thiết bị liên tục (Chattering) khi mặt nước dập dềnh quanh ngưỡng", 
            fontsize=9.5, style='italic', ha='center', color='#475569')

    states = [
        ("NORMAL\n(An Toàn)", 1.8, 4.5, '#10b981', '#ecfdf5', "Mực nước: 0 - 20%\nKhô ráo / Tạnh mưa"),
        ("WARNING\n(Cảnh Báo)", 4.6, 4.5, '#f59e0b', '#fffbeb', "Mực nước: 21 - 40%\nHoặc mưa nhỏ"),
        ("DANGER\n(Nguy Cơ Ngập)", 7.4, 4.5, '#f97316', '#fff7ed', "Mực nước: 41 - 70%\nHoặc mưa to"),
        ("CRITICAL\n(Nguy Cấp)", 10.2, 4.5, '#ef4444', '#fef2f2', "Mực nước: 71 - 100%\nHoặc ngập cảm biến")
    ]

    for title, x, y, border, bg, desc in states:
        box = FancyBboxPatch((x - 1.1, y - 0.7), 2.2, 1.4, boxstyle="round,pad=0.1,rounding_size=0.2",
                             facecolor=bg, edgecolor=border, lw=2.2)
        ax.add_patch(box)
        ax.text(x, y + 0.25, title, fontsize=9.5, fontweight='bold', ha='center', va='center', color=border)
        ax.text(x, y - 0.25, desc, fontsize=7.5, ha='center', va='center', color='#334155')

    # Forward arrows (Rising water)
    ax.add_patch(FancyArrowPatch((2.9, 4.8), (3.5, 4.8), arrowstyle='->', mutation_scale=14, color='#f59e0b', lw=2))
    ax.text(3.2, 5.15, "Nước ≥ 21%\nhoặc mưa nhỏ", fontsize=7.5, ha='center', color='#b45309')

    ax.add_patch(FancyArrowPatch((5.7, 4.8), (6.3, 4.8), arrowstyle='->', mutation_scale=14, color='#f97316', lw=2))
    ax.text(6.0, 5.15, "Nước ≥ 41%\nhoặc mưa to", fontsize=7.5, ha='center', color='#c2410c')

    ax.add_patch(FancyArrowPatch((8.5, 4.8), (9.1, 4.8), arrowstyle='->', mutation_scale=14, color='#ef4444', lw=2))
    ax.text(8.8, 5.15, "Nước ≥ 71%\nhoặc ngập sensor", fontsize=7.5, ha='center', color='#b91c1c')

    # Backward arrows (Falling water with Hysteresis)
    ax.add_patch(FancyArrowPatch((9.1, 4.2), (8.5, 4.2), arrowstyle='->', mutation_scale=14, color='#ea580c', lw=2, linestyle='--'))
    ax.text(8.8, 3.8, "Nước < 71%\nvà hết ngập sensor", fontsize=7.5, ha='center', color='#c2410c')

    ax.add_patch(FancyArrowPatch((6.3, 4.2), (5.7, 4.2), arrowstyle='->', mutation_scale=14, color='#d97706', lw=2, linestyle='--'))
    ax.text(6.0, 3.8, "Nước rút < 40%\n(Dải trễ an toàn)", fontsize=7.5, ha='center', color='#b45309')

    ax.add_patch(FancyArrowPatch((3.5, 4.2), (2.9, 4.2), arrowstyle='->', mutation_scale=14, color='#059669', lw=2, linestyle='--'))
    ax.text(3.2, 3.8, "Nước rút < 20%\nvà tạnh mưa", fontsize=7.5, ha='center', color='#047857')

    # Explain Hysteresis Box
    hyp_box = FancyBboxPatch((1.5, 0.8), 9.0, 1.8, boxstyle="round,pad=0.1,rounding_size=0.2",
                             facecolor='#f8fafc', edgecolor='#0284c7', lw=1.5)
    ax.add_patch(hyp_box)
    ax.text(6.0, 2.2, "Ý NGHĨA KỸ THUẬT CỦA DẢI TRỄ (HYSTERESIS):", fontsize=9.5, fontweight='bold', ha='center', color='#0369a1')
    ax.text(6.0, 1.8, "• Bơm BẬT khi nước chạm 41%, nhưng CHỈ TẮT khi nước rút sâu hẳn xuống < 40%.", fontsize=8.5, ha='center', color='#1e293b')
    ax.text(6.0, 1.5, "• Độ chênh lệch biên (Delta = 1% ~ 0.45cm) triệt tiêu hoàn toàn sóng cơ học trên mặt nước.", fontsize=8.5, ha='center', color='#1e293b')
    ax.text(6.0, 1.2, "• Ngăn ngừa relay và động cơ bị đóng ngắt liên hồi gây hỏng tiếp điểm hoặc sụt áp vi điều khiển.", fontsize=8.5, ha='center', color='#1e293b')

    save_fig(fig, "uc02_fsm_hysteresis.png")

# -------------------------------------------------------------
# 4. UC03 DIAGRAM: Điều khiển Máy Bơm Thoát Nước (Relay High-Z)
# -------------------------------------------------------------
def make_uc03():
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    ax.text(6, 5.5, "UC03: TỰ ĐỘNG ĐIỀU KHIỂN MÁY BƠM THOÁT NƯỚC (RELAY HIGH-Z)", fontsize=14, fontweight='bold', ha='center', color='#0f172a')
    ax.text(6, 5.15, "Sử dụng kỹ thuật High-Z triệt tiêu dòng rò 3.3V-5V Optocoupler, điều khiển bơm an toàn", 
            fontsize=9.5, style='italic', ha='center', color='#475569')

    boxes = [
        ("Trạng Thái FSM\nDANGER / CRITICAL\n(Nước ≥ 41% hoặc mưa to)", 1.8, 3.2, 2.6, 1.4, '#fee2e2', '#ef4444'),
        ("ESP32 Thuật Toán\nKiểm tra AUTO MODE\n& Ngưỡng Hysteresis", 5.0, 3.2, 2.6, 1.4, '#e0f2fe', '#0284c7'),
        ("Kỹ Thuật High-Z\n• BẬT: OUTPUT + LOW\n• TẮT: INPUT (Thả nổi)", 8.2, 3.2, 2.6, 1.4, '#fef3c7', '#d97706'),
        ("Khối Chấp Hành\nModule Relay 5V\nMáy bơm chìm 5V", 10.9, 3.2, 1.8, 1.4, '#f0fdf4', '#16a34a')
    ]

    for text, x, y, w, h, bg, border in boxes:
        box = FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.1,rounding_size=0.15",
                             facecolor=bg, edgecolor=border, lw=2)
        ax.add_patch(box)
        ax.text(x, y, text, fontsize=8.5, fontweight='bold', ha='center', va='center', color='#1e293b')

    # Arrows
    ax.add_patch(FancyArrowPatch((3.1, 3.2), (3.7, 3.2), arrowstyle='->', mutation_scale=14, color='#ef4444', lw=2))
    ax.add_patch(FancyArrowPatch((6.3, 3.2), (6.9, 3.2), arrowstyle='->', mutation_scale=14, color='#0284c7', lw=2))
    ax.add_patch(FancyArrowPatch((9.5, 3.2), (10.0, 3.2), arrowstyle='->', mutation_scale=14, color='#d97706', lw=2))

    # Note
    note_box = FancyBboxPatch((1.5, 0.8), 9.0, 1.3, boxstyle="round,pad=0.1,rounding_size=0.15",
                              facecolor='#f8fafc', edgecolor='#64748b', lw=1.2)
    ax.add_patch(note_box)
    ax.text(6.0, 1.6, "Ưu điểm kỹ thuật High-Z:", fontsize=9, fontweight='bold', ha='center', color='#334155')
    ax.text(6.0, 1.25, "ESP32 cấp 3.3V lên cực IN relay 5V vẫn có dòng rò ~1.5mA làm relay không ngắt hẳn.", fontsize=8, ha='center', color='#1e293b')
    ax.text(6.0, 1.0, "Chuyển pinMode(PIN_RELAY, INPUT) ngắt hoàn toàn mạch, bơm ngừng dứt điểm 100%.", fontsize=8, ha='center', color='#1e293b')

    save_fig(fig, "uc03_pump_control.png")

# -------------------------------------------------------------
# 5. UC04 DIAGRAM: Điều khiển Van Thoát Lũ (Servo SG90)
# -------------------------------------------------------------
def make_uc04():
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    ax.text(6, 5.5, "UC04: TỰ ĐỘNG ĐIỀU KHIỂN GÓC MỞ VAN THOÁT LŨ (SERVO SG90)", fontsize=14, fontweight='bold', ha='center', color='#0f172a')
    ax.text(6, 5.15, "Điều chế độ rộng xung PWM (500us - 2400us) kéo mở cửa van theo từng cấp độ lũ", 
            fontsize=9.5, style='italic', ha='center', color='#475569')

    levels = [
        ("NORMAL / WARNING\n(Nước ≤ 40%)", "0% Độ Mở\nGóc 0°", "Cửa van ĐÓNG KÍN\nGiữ nước hồ thu", '#10b981', '#ecfdf5', 2.2),
        ("DANGER\n(Nước 41 - 70%)", "50% Độ Mở\nGóc 90°", "Xả lũ mức vừa\nĐiều tiết dòng chảy", '#f97316', '#fff7ed', 6.0),
        ("CRITICAL\n(Nước ≥ 71%)", "100% Độ Mở\nGóc 180°", "Xả lũ tối đa\nThoát nước khẩn cấp", '#ef4444', '#fef2f2', 9.8)
    ]

    for state, angle, act, col, bg, x in levels:
        box = FancyBboxPatch((x - 1.6, 2.2), 3.2, 2.3, boxstyle="round,pad=0.1,rounding_size=0.2",
                             facecolor=bg, edgecolor=col, lw=2.2)
        ax.add_patch(box)
        ax.text(x, 4.0, state, fontsize=9.5, fontweight='bold', ha='center', color=col)
        ax.text(x, 3.3, angle, fontsize=12, fontweight='bold', ha='center', color='#1e293b')
        ax.text(x, 2.6, act, fontsize=8, ha='center', color='#475569')

    # Lower info
    ax.text(6.0, 1.2, "ESP32 điều khiển PWM chân GPIO 27 (D27) qua thư viện ESP32Servo phần cứng", 
            fontsize=9.5, fontweight='bold', ha='center', color='#0369a1')
    ax.text(6.0, 0.8, "Khởi tạo góc 0° khi khởi động. Chuyển góc êm ái, phản hồi tức thời theo trạng thái FSM.", 
            fontsize=8.5, ha='center', color='#64748b')

    save_fig(fig, "uc04_valve_control.png")

# -------------------------------------------------------------
# 6. UC05 DIAGRAM: Cảnh báo LED & Buzzer
# -------------------------------------------------------------
def make_uc05():
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    ax.text(6, 6.0, "UC05: TỰ ĐỘNG PHÁT TÍN HIỆU CẢNH BÁO TẠI TRẠM (LED & BUZZER)", fontsize=14, fontweight='bold', ha='center', color='#0f172a')
    ax.text(6, 5.65, "Hệ thống cảnh báo âm thanh & ánh sáng 4 cấp độ non-blocking điều khiển bằng millis()", 
            fontsize=9.5, style='italic', ha='center', color='#475569')

    tiers = [
        ("NORMAL\n(An Toàn)", "LED XANH (D21) Bật\nLED Vàng, Đỏ: Tắt", "Còi YÊN LẶNG\n(noTone / 0Hz)", '#10b981', '#ecfdf5', 1.8),
        ("WARNING\n(Cảnh Báo)", "LED VÀNG (D19) Bật\nLED Xanh, Đỏ: Tắt", "Bíp nhẹ ngắt quãng\n1000Hz (120ms / 1.5s)", '#f59e0b', '#fffbeb', 4.6),
        ("DANGER\n(Nguy Cơ)", "LED ĐỎ (D18) Bật\nLED Xanh, Vàng: Tắt", "Báo dồn dập liên hồi\n1800Hz (150ms / 300ms)", '#f97316', '#fff7ed', 7.4),
        ("CRITICAL\n(Nguy Cấp)", "LED ĐỎ Chớp Nháy\nChu kỳ nhanh 100ms", "Còi HÚ LIÊN TỤC\n2500Hz không ngắt", '#ef4444', '#fef2f2', 10.2)
    ]

    for state, led, buzzer, col, bg, x in tiers:
        box = FancyBboxPatch((x - 1.2, 1.8), 2.4, 3.4, boxstyle="round,pad=0.1,rounding_size=0.2",
                             facecolor=bg, edgecolor=col, lw=2.2)
        ax.add_patch(box)
        ax.text(x, 4.7, state, fontsize=9.5, fontweight='bold', ha='center', color=col)
        ax.text(x, 3.6, f"CHỈ THỊ ÁNH SÁNG:\n{led}", fontsize=8, ha='center', color='#1e293b')
        ax.text(x, 2.4, f"CẢNH BÁO ÂM THANH:\n{buzzer}", fontsize=8, ha='center', color='#1e293b')

    ax.text(6.0, 0.9, "Cơ chế Non-blocking: Sử dụng biến thời gian now % T để tạo nhịp bíp mà không làm treo Web Server", 
            fontsize=9, fontweight='bold', ha='center', color='#0284c7')

    save_fig(fig, "uc05_signaling_buzzer_led.png")

# -------------------------------------------------------------
# 7. UC06 DIAGRAM: Failsafe to AUTO khi mất mạng
# -------------------------------------------------------------
def make_uc06():
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    ax.text(6, 5.5, "UC06: TỰ ĐỘNG CHUYỂN ĐỔI AN TOÀN (FAILSAFE TO AUTO MODE)", fontsize=14, fontweight='bold', ha='center', color='#0f172a')
    ax.text(6, 5.15, "Đảm bảo tính tự trị của trạm nhúng khi mất kết nối mạng hoặc mất giám sát từ xa", 
            fontsize=9.5, style='italic', ha='center', color='#475569')

    boxes = [
        ("Trạng Thái Ban Đầu\nĐang ở MANUAL MODE\n(Người điều khiển thủ công)", 1.8, 3.2, 2.6, 1.5, '#e0f2fe', '#0284c7'),
        ("Sự Cố Mạng Xảy Ra\n• Mất sóng Wi-Fi\n• Mất Heartbeat Client\n• Quá thời gian Timeout", 5.0, 3.2, 2.6, 1.5, '#fee2e2', '#ef4444'),
        ("Cơ Chế Failsafe ESP32\n• Phát còi cảnh báo lỗi\n• Cưỡng chế về AUTO\n• Khóa can thiệp thủ công", 8.2, 3.2, 2.6, 1.5, '#fef3c7', '#d97706'),
        ("Hệ Thống An Toàn\nTrạm tự động bơm & xả\nTránh vỡ đập, ngập úng", 10.9, 3.2, 1.8, 1.5, '#f0fdf4', '#16a34a')
    ]

    for text, x, y, w, h, bg, border in boxes:
        box = FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.1,rounding_size=0.15",
                             facecolor=bg, edgecolor=border, lw=2)
        ax.add_patch(box)
        ax.text(x, y, text, fontsize=8.5, fontweight='bold', ha='center', va='center', color='#1e293b')

    ax.add_patch(FancyArrowPatch((3.1, 3.2), (3.7, 3.2), arrowstyle='->', mutation_scale=14, color='#0284c7', lw=2))
    ax.add_patch(FancyArrowPatch((6.3, 3.2), (6.9, 3.2), arrowstyle='->', mutation_scale=14, color='#ef4444', lw=2))
    ax.add_patch(FancyArrowPatch((9.5, 3.2), (10.0, 3.2), arrowstyle='->', mutation_scale=14, color='#d97706', lw=2))

    ax.text(6.0, 1.2, "Ý nghĩa then chốt trong hệ thống thời gian thực: Vi điều khiển luôn là trung tâm quyết định an toàn,", 
            fontsize=8.5, ha='center', color='#334155')
    ax.text(6.0, 0.9, "không bị phụ thuộc hoặc tê liệt nếu kết nối không dây bị gián đoạn ngoài thực địa.", 
            fontsize=8.5, ha='center', color='#334155')

    save_fig(fig, "uc06_network_failsafe.png")

# -------------------------------------------------------------
# 8. UC07 DIAGRAM: Telemetry & API
# -------------------------------------------------------------
def make_uc07():
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    ax.text(6, 5.5, "UC07: TRUYỀN NHẬN DỮ LIỆU THỜI GIAN THỰC (TELEMETRY & REST API)", fontsize=14, fontweight='bold', ha='center', color='#0f172a')
    ax.text(6, 5.15, "Kiến trúc máy chủ HTTP Server cổng 80 đóng gói JSON truyền tốc độ cao qua Wi-Fi", 
            fontsize=9.5, style='italic', ha='center', color='#475569')

    # Client Box
    c_box = FancyBboxPatch((0.8, 1.5), 2.5, 2.8, boxstyle="round,pad=0.1,rounding_size=0.2",
                           facecolor='#f8fafc', edgecolor='#64748b', lw=2)
    ax.add_patch(c_box)
    ax.text(2.05, 3.9, "Trình Duyệt Web Client\n(Máy tính / Điện thoại)", fontsize=9.5, fontweight='bold', ha='center', color='#1e293b')
    ax.text(2.05, 3.0, "• fetch('/api/status')\n• Định kỳ 1000ms\n• fetch('/api/control')", fontsize=8.5, ha='center', color='#475569')

    # ESP32 Server Box
    s_box = FancyBboxPatch((8.7, 1.5), 2.8, 2.8, boxstyle="round,pad=0.1,rounding_size=0.2",
                           facecolor='#e0f2fe', edgecolor='#0284c7', lw=2)
    ax.add_patch(s_box)
    ax.text(10.1, 3.9, "ESP32 Web Server\n(WebServer.h - Port 80)", fontsize=9.5, fontweight='bold', ha='center', color='#0369a1')
    ax.text(10.1, 3.0, "• SoftAP / Station\n• handleRoot()\n• handleStatusApi()\n• handleControlApi()", fontsize=8.5, ha='center', color='#1e293b')

    # Endpoints in Middle
    ax.add_patch(FancyArrowPatch((3.4, 3.6), (8.6, 3.6), arrowstyle='->', mutation_scale=14, color='#0284c7', lw=2))
    ax.text(6.0, 3.85, "GET /api/status (Yêu cầu dữ liệu định kỳ)", fontsize=8.5, fontweight='bold', ha='center', color='#0369a1')

    ax.add_patch(FancyArrowPatch((8.6, 2.9), (3.4, 2.9), arrowstyle='->', mutation_scale=14, color='#10b981', lw=2))
    ax.text(6.0, 3.1, '200 OK: {"water":45, "dist":29.8, "rain":true, "state":"DANGER", ...}', fontsize=7.5, ha='center', color='#047857', family='monospace')

    ax.add_patch(FancyArrowPatch((3.4, 2.1), (8.6, 2.1), arrowstyle='->', mutation_scale=14, color='#f97316', lw=2))
    ax.text(6.0, 2.35, "GET /api/control?action=pump_toggle (Gửi lệnh điều khiển)", fontsize=8.5, fontweight='bold', ha='center', color='#c2410c')

    save_fig(fig, "uc07_telemetry_api.png")

# -------------------------------------------------------------
# 9. UC08 DIAGRAM: Web Dashboard UI
# -------------------------------------------------------------
def make_uc08():
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.5)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    ax.text(6, 6.0, "UC08: GIÁM SÁT TRẠNG THÁI TRẠM TỪ XA TRÊN WEB DASHBOARD", fontsize=14, fontweight='bold', ha='center', color='#0f172a')
    ax.text(6, 5.65, "Giao diện Dark Glassmorphism cập nhật Single Page Application (SPA) không tải lại trang", 
            fontsize=9.5, style='italic', ha='center', color='#475569')

    cards = [
        ("CARD 1: MỰC NƯỚC", "• Tỷ lệ % (0 - 100%)\n• Khoảng cách thô (cm)\n• Thanh tiến trình đổi màu\n  (Xanh -> Vàng -> Đỏ)", 2.0, 3.3, '#38bdf8'),
        ("CARD 2: CẢNH BÁO", "• Badge trạng thái FSM\n• Chế độ AUTO/MANUAL\n• Cảm biến mưa (ADC)\n• Đánh giá thời tiết", 6.0, 3.3, '#f59e0b'),
        ("CARD 3: THIẾT BỊ", "• Máy bơm 5V: ON/OFF\n• Van xả SG90: 0/50/100%\n• Còi Buzzer: Hú/Dồn/Tắt\n• Chỉ thị tức thời", 10.0, 3.3, '#10b981')
    ]

    for title, desc, x, y, col in cards:
        box = FancyBboxPatch((x - 1.7, y - 1.5), 3.4, 3.0, boxstyle="round,pad=0.1,rounding_size=0.2",
                             facecolor='#0f172a', edgecolor=col, lw=2)
        ax.add_patch(box)
        ax.text(x, y + 1.1, title, fontsize=9.5, fontweight='bold', ha='center', color=col)
        ax.text(x, y - 0.2, desc, fontsize=8.5, ha='center', color='#f8fafc')

    ax.text(6.0, 1.0, "Người vận hành giám sát trạm từ xa qua laptop hoặc smartphone kết nối Wi-Fi mà không cần màn hình LCD vật lý", 
            fontsize=9, fontweight='bold', ha='center', color='#475569')

    save_fig(fig, "uc08_web_dashboard.png")

# -------------------------------------------------------------
# 10. UC09 DIAGRAM: Chuyển đổi AUTO / MANUAL
# -------------------------------------------------------------
def make_uc09():
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    ax.text(6, 5.5, "UC09: CHUYỂN ĐỔI CHẾ ĐỘ VẬN HÀNH TỪ XA (AUTO / MANUAL)", fontsize=14, fontweight='bold', ha='center', color='#0f172a')
    ax.text(6, 5.15, "Phân quyền điều khiển linh hoạt giữa vi điều khiển tự động và người quản lý", 
            fontsize=9.5, style='italic', ha='center', color='#475569')

    box_auto = FancyBboxPatch((1.0, 2.0), 4.2, 2.5, boxstyle="round,pad=0.1,rounding_size=0.2",
                              facecolor='#ecfdf5', edgecolor='#10b981', lw=2)
    ax.add_patch(box_auto)
    ax.text(3.1, 4.0, "CHẾ ĐỘ TỰ ĐỘNG (AUTO MODE)", fontsize=10, fontweight='bold', ha='center', color='#047857')
    ax.text(3.1, 3.1, "• ESP32 toàn quyền quyết định\n• FSM tự động bật/tắt bơm\n• Tự động xoay góc van xả lũ\n• Khóa nút bấm can thiệp web", fontsize=8.5, ha='center', color='#1e293b')

    box_manual = FancyBboxPatch((6.8, 2.0), 4.2, 2.5, boxstyle="round,pad=0.1,rounding_size=0.2",
                                facecolor='#fffbeb', edgecolor='#f59e0b', lw=2)
    ax.add_patch(box_manual)
    ax.text(8.9, 4.0, "CHẾ ĐỘ THỦ CÔNG (MANUAL MODE)", fontsize=10, fontweight='bold', ha='center', color='#b45309')
    ax.text(8.9, 3.1, "• Tạm dừng quyền tự quyết FSM\n• Mở khóa các nút điều khiển web\n• Cho phép bật/tắt bơm cưỡng chế\n• Cho phép chọn góc mở van", fontsize=8.5, ha='center', color='#1e293b')

    # Switch Arrows
    ax.add_patch(FancyArrowPatch((5.3, 3.5), (6.7, 3.5), arrowstyle='->', mutation_scale=14, color='#3b82f6', lw=2))
    ax.text(6.0, 3.75, "Ấn Đổi Chế Độ", fontsize=8, fontweight='bold', ha='center', color='#1d4ed8')

    ax.add_patch(FancyArrowPatch((6.7, 2.7), (5.3, 2.7), arrowstyle='->', mutation_scale=14, color='#10b981', lw=2))
    ax.text(6.0, 2.4, "Trả về AUTO", fontsize=8, fontweight='bold', ha='center', color='#047857')

    ax.text(6.0, 1.0, "Lệnh truyền qua HTTP: /api/control?action=mode_toggle -> ESP32 đảo cờ isAutoMode", 
            fontsize=9, fontweight='bold', ha='center', color='#64748b')

    save_fig(fig, "uc09_mode_switch.png")

# -------------------------------------------------------------
# 11. UC10 DIAGRAM: Điều khiển cưỡng chế (Manual Override)
# -------------------------------------------------------------
def make_uc10():
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    ax.text(6, 5.5, "UC10: ĐIỀU KHIỂN CƯỠNG CHẾ THIẾT BỊ CHẤP HÀNH TỪ WEB (MANUAL OVERRIDE)", fontsize=14, fontweight='bold', ha='center', color='#0f172a')
    ax.text(6, 5.15, "Can thiệp trực tiếp máy bơm và van xả phục vụ bảo trì, xả cặn hoặc ứng phó khẩn cấp", 
            fontsize=9.5, style='italic', ha='center', color='#475569')

    steps = [
        ("1. Người Dùng Bấm Nút\n• Bật/Tắt Bơm (pump_toggle)\n• Van 0% / 50% / 100%", 1.8, 3.2, 2.6, 1.5, '#f8fafc', '#64748b'),
        ("2. Kiểm Tra Điều Kiện\nisAutoMode == false ?\n• Hợp lệ: Tiếp nhận\n• Từ chối nếu đang AUTO", 5.0, 3.2, 2.6, 1.5, '#fef3c7', '#d97706'),
        ("3. Xuất Tín Hiệu GPIO\n• Kích tiếp điểm Relay bơm\n• Xuất xung PWM xoay Servo", 8.2, 3.2, 2.6, 1.5, '#e0f2fe', '#0284c7'),
        ("4. Phản Hồi Web\n200 OK + Cập nhật\ntrực tiếp trên UI", 10.9, 3.2, 1.8, 1.5, '#f0fdf4', '#16a34a')
    ]

    for text, x, y, w, h, bg, border in steps:
        box = FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.1,rounding_size=0.15",
                             facecolor=bg, edgecolor=border, lw=2)
        ax.add_patch(box)
        ax.text(x, y, text, fontsize=8.5, fontweight='bold', ha='center', va='center', color='#1e293b')

    ax.add_patch(FancyArrowPatch((3.1, 3.2), (3.7, 3.2), arrowstyle='->', mutation_scale=14, color='#64748b', lw=2))
    ax.add_patch(FancyArrowPatch((6.3, 3.2), (6.9, 3.2), arrowstyle='->', mutation_scale=14, color='#d97706', lw=2))
    ax.add_patch(FancyArrowPatch((9.5, 3.2), (10.0, 3.2), arrowstyle='->', mutation_scale=14, color='#0284c7', lw=2))

    ax.text(6.0, 1.1, "Loại bỏ nút nhấn vật lý giúp trạm chống chịu tốt với độ ẩm cao, bụi bẩn và ngập nước ngoài công trường.", 
            fontsize=9, fontweight='bold', ha='center', color='#334155')

    save_fig(fig, "uc10_manual_override.png")

# Run all
if __name__ == "__main__":
    print("Generating diagrams...")
    make_uc_overall()
    make_uc01()
    make_uc02()
    make_uc03()
    make_uc04()
    make_uc05()
    make_uc06()
    make_uc07()
    make_uc08()
    make_uc09()
    make_uc10()
    print("All 11 diagrams created successfully!")
