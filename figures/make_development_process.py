import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def make_development_process_diagram():
    fig_dir = 'figures'
    report_fig_dir = os.path.join('report', 'figures')
    os.makedirs(fig_dir, exist_ok=True)
    os.makedirs(report_fig_dir, exist_ok=True)

    # Set clean, legible font family
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Calibri']
    plt.rcParams['font.family'] = 'sans-serif'

    # Dimensions designed to match \textwidth (160mm = 6.30 in) and vertical budget on Page 29
    fig_w = 6.30
    fig_h = 7.35
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Main title and subtitle at top
    ax.text(fig_w / 2, 7.20, 'QUY TRÌNH PHÁT TRIỂN TOÀN DIỆN HỆ THỐNG FLOODGUARD',
            fontsize=11.5, fontweight='bold', ha='center', va='center', color='#0f172a')
    ax.text(fig_w / 2, 7.00, 'Mô hình 5 giai đoạn kỹ thuật gắn kết chặt chẽ với cấu trúc báo cáo',
            fontsize=9.2, style='italic', ha='center', va='center', color='#475569')

    stages = [
        {
            'step': 'BƯỚC 1',
            'title': 'PHÂN TÍCH YÊU CẦU & MÔ HÌNH HÓA USE CASE',
            'chapter': 'Ánh xạ: Chương 1',
            'items': [
                '• Khảo sát ngập úng đô thị; xác lập chỉ tiêu WCRT ≤ 250 ms.',
                '• Xây dựng 10 Use Case UML (UC01–UC10) chuẩn hóa.',
                '• Ràng buộc phi chức năng: Task Watchdog & an toàn Failsafe.'
            ],
            'output': 'Đầu ra: Đặc tả yêu cầu kỹ thuật & 10 Use Case UML chuẩn hóa.'
        },
        {
            'step': 'BƯỚC 2',
            'title': 'THIẾT KẾ HỆ THỐNG (PHẦN CỨNG, THUẬT TOÁN & WEB)',
            'chapter': 'Ánh xạ: Chương 2, 3 & 4',
            'items': [
                '• Kiến trúc 5 khối, sơ đồ nguyên lý IEC & ma trận GPIO.',
                '• Thiết kế FSM 4 trạng thái, dải trễ Hysteresis & lọc trung vị.',
                '• Thiết kế Web Dashboard thời gian thực và đặc tả REST API.'
            ],
            'output': 'Đầu ra: Sơ đồ nguyên lý IEC, Lưu đồ FSM & REST API.'
        },
        {
            'step': 'BƯỚC 3',
            'title': 'CÀI ĐẶT, LẬP TRÌNH & TÍCH HỢP TOÀN DIỆN',
            'chapter': 'Ánh xạ: Chương 2, 3 & 4',
            'items': [
                '• Lập trình firmware ESP32 theo cơ chế millis() phi chặn.',
                '• Đấu nối sa bàn: Cảm biến siêu âm, mưa, Relay, Servo & còi.',
                '• Cấu hình Task Watchdog (TWDT 3 s), SoftAP & Web nhúng.'
            ],
            'output': 'Đầu ra: Firmware hoàn chỉnh, Sa bàn & Web Server nhúng.'
        },
        {
            'step': 'BƯỚC 4',
            'title': 'CHẠY THỬ, ĐO KIỂM & KIỂM THỬ THỰC NGHIỆM',
            'chapter': 'Ánh xạ: Chương 5',
            'items': [
                '• Chạy thử mô phỏng Wokwi và thử nghiệm sa bàn với nước thật.',
                '• Đo kiểm thời gian đáp ứng (WCRT = 203 ms ≤ 250 ms).',
                '• Kiểm thử ngoại lệ: Mất mạng (Failsafe 30 s), kẹt van, dâng nước.'
            ],
            'output': 'Đầu ra: Báo cáo đo kiểm WCRT & Biên bản thử nghiệm sa bàn.'
        },
        {
            'step': 'BƯỚC 5',
            'title': 'ĐÁNH GIÁ, TỔNG KẾT & ĐỊNH HƯỚNG HOÀN THIỆN',
            'chapter': 'Ánh xạ: Chương 6',
            'items': [
                '• Đối chiếu 100% mục tiêu: Vận hành tự trị & an toàn Failsafe.',
                '• Đánh giá ưu điểm mô hình và phân tích hạn chế kỹ thuật.',
                '• Đề xuất nâng cấp: Cảm biến radar, vi mạch mã hóa TLS & OTA.'
            ],
            'output': 'Đầu ra: Báo cáo nghiệm thu dự án & Lộ trình nâng cấp.'
        }
    ]

    card_x = 0.08
    card_w = 5.08
    card_h = 1.25
    gap = 0.11
    start_y = 6.82

    for i, s in enumerate(stages):
        sy = start_y - (i + 1) * card_h - i * gap
        sh = card_h
        s['y'] = sy
        s['h'] = sh

        # Outer card container
        rect = patches.FancyBboxPatch((card_x, sy), card_w, sh,
                                     boxstyle='round,pad=0.0,rounding_size=0.08',
                                     facecolor='#ffffff', edgecolor='#1e293b', linewidth=1.2, zorder=2)
        ax.add_patch(rect)

        # Header bar background
        hbar_h = 0.46
        hbar = patches.FancyBboxPatch((card_x, sy + sh - hbar_h), card_w, hbar_h,
                                     boxstyle='round,pad=0.0,rounding_size=0.08',
                                     facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.0, zorder=3)
        ax.add_patch(hbar)

        # Line 1: Step Badge on left
        badge_w = 0.82
        badge_h = 0.19
        badge_y = sy + sh - 0.23
        badge = patches.FancyBboxPatch((card_x + 0.10, badge_y), badge_w, badge_h,
                                      boxstyle='round,pad=0.0,rounding_size=0.04',
                                      facecolor='#0f172a', edgecolor='#0f172a', linewidth=0.8, zorder=4)
        ax.add_patch(badge)
        ax.text(card_x + 0.10 + badge_w / 2, badge_y + badge_h / 2, s['step'],
                fontsize=9.0, fontweight='bold', ha='center', va='center', color='#ffffff', zorder=5)

        # Line 1: Chapter mapping chip on right
        chip_w = 1.38 if '&' in s['chapter'] else 1.15
        chip_h = 0.19
        chip_x = card_x + card_w - chip_w - 0.10
        chip_y = badge_y
        chip = patches.FancyBboxPatch((chip_x, chip_y), chip_w, chip_h,
                                     boxstyle='round,pad=0.0,rounding_size=0.04',
                                     facecolor='#e2e8f0', edgecolor='#94a3b8', linewidth=0.8, zorder=4)
        ax.add_patch(chip)
        ax.text(chip_x + chip_w / 2, chip_y + chip_h / 2, s['chapter'],
                fontsize=8.2, fontweight='bold', style='italic', ha='center', va='center', color='#1e293b', zorder=5)

        # Line 2: Stage Title below Badge & Chip
        title_y = sy + sh - 0.35
        ax.text(card_x + 0.12, title_y, s['title'],
                fontsize=9.6, fontweight='bold', ha='left', va='center', color='#0f172a', zorder=5)

        # Bullet items inside card
        first_item_y = sy + sh - hbar_h - 0.12
        item_spacing = 0.16
        for idx, item in enumerate(s['items']):
            iy = first_item_y - idx * item_spacing
            ax.text(card_x + 0.12, iy, item,
                    fontsize=9.0, ha='left', va='center', color='#1e293b', zorder=4)

        # Output box at bottom of card
        out_h = 0.20
        out_y = sy + 0.05
        out_rect = patches.Rectangle((card_x + 0.08, out_y), card_w - 0.16, out_h,
                                     facecolor='#f1f5f9', edgecolor='#94a3b8', linewidth=0.7, linestyle='--', zorder=3)
        ax.add_patch(out_rect)
        ax.text(card_x + card_w / 2, out_y + out_h / 2, s['output'],
                fontsize=8.5, fontweight='bold', style='italic', ha='center', va='center', color='#334155', zorder=4)

    # Downward connecting arrows between steps
    for i in range(len(stages) - 1):
        top_y = stages[i]['y']
        bot_y = stages[i+1]['y'] + stages[i+1]['h']
        arrow_x = card_x + card_w / 2

        ax.annotate('', xy=(arrow_x, bot_y), xytext=(arrow_x, top_y),
                    arrowprops=dict(facecolor='#0f172a', edgecolor='#0f172a', width=1.8, headwidth=6.5, headlength=6.0),
                    zorder=6)

    # Feedback loop: From Step 4 back to Step 3 and Step 2
    loop_x = 6.20
    step4_y = stages[3]['y'] + stages[3]['h'] / 2
    step3_y = stages[2]['y'] + stages[2]['h'] / 2
    step2_y = stages[1]['y'] + stages[1]['h'] / 2

    # Horizontal exit line from Step 4
    ax.plot([card_x + card_w, loop_x], [step4_y, step4_y], color='#0f172a', lw=1.5, ls='-', zorder=5)
    # Vertical spine going up
    ax.plot([loop_x, loop_x], [step4_y, step2_y], color='#0f172a', lw=1.5, ls='-', zorder=5)

    # Arrow branch 1 to Step 3
    ax.annotate('', xy=(card_x + card_w, step3_y), xytext=(loop_x, step3_y),
                arrowprops=dict(facecolor='#0f172a', edgecolor='#0f172a', width=1.4, headwidth=5.5, headlength=5.0),
                zorder=6)

    # Arrow branch 2 to Step 2
    ax.annotate('', xy=(card_x + card_w, step2_y), xytext=(loop_x, step2_y),
                arrowprops=dict(facecolor='#0f172a', edgecolor='#0f172a', width=1.4, headwidth=5.5, headlength=5.0),
                zorder=6)

    # Feedback label box in the middle of loop
    fb_box_x = 5.20
    fb_box_w = 0.94
    fb_box_y = step3_y + 0.15
    fb_box_h = 0.90
    fb_box = patches.FancyBboxPatch((fb_box_x, fb_box_y), fb_box_w, fb_box_h,
                                    boxstyle='round,pad=0.0,rounding_size=0.06',
                                    facecolor='#ffffff', edgecolor='#0f172a', linewidth=1.0, zorder=6)
    ax.add_patch(fb_box)
    ax.text(fb_box_x + fb_box_w / 2, fb_box_y + 0.70, 'VÒNG LẶP\nPHẢN HỒI',
            fontsize=8.0, fontweight='bold', ha='center', va='center', color='#0f172a', zorder=7)
    ax.text(fb_box_x + fb_box_w / 2, fb_box_y + 0.28, '• Hiệu chuẩn\n• Tinh chỉnh\n• Tối ưu hóa',
            fontsize=7.2, ha='center', va='center', color='#334155', zorder=7)

    plt.tight_layout()
    p1 = os.path.join(fig_dir, 'project_development_process.png')
    p2 = os.path.join(report_fig_dir, 'project_development_process.png')
    fig.savefig(p1, dpi=300, bbox_inches='tight')
    fig.savefig(p2, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'Successfully generated:\n- {p1}\n- {p2}')

if __name__ == '__main__':
    make_development_process_diagram()
