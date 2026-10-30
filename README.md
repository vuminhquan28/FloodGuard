# 🌊 FloodGuard - Hệ Thống Giám Sát & Chống Ngập Thông Minh

Hệ thống IoT ứng dụng **ESP32** kết hợp cảm biến siêu âm HC-SR04, cảm biến mưa, động cơ Servo điều khiển van xả, Relay điều khiển máy bơm, còi cảnh báo và hệ thống Web Server giám sát qua Wi-Fi thời gian thực (hiển thị trực tiếp trên máy tính / điện thoại).

---

## 🛠️ Danh Sách Linh Kiện & Bảng Phân Công Chân (GPIO Mapping)

### 1. Bảng phân công chân phần cứng (GPIO Mapping)
| STT | Thiết bị / Module | Chân tín hiệu | GPIO ESP32 | Vị trí Breadboard | Ghi chú |
| :-: | :--- | :--- | :--- | :--- | :--- |
| 1 | **HC-SR04** (Siêu âm) | Trig | `GPIO 13` (D13) | Lỗ g38 bo trái | Phát xung siêu âm đo mặt nước |
| 1 | **HC-SR04** (Siêu âm) | Echo | `GPIO 12` (D12) | Lỗ g37 bo trái | Nhận xung phản hồi (nối tiếp trở hạn dòng) |
| 2 | **Cảm biến mưa** | DO (Digital) | `GPIO 34` (D34) | Lỗ b31 bo phải | Phát hiện mưa/khô – Input-only |
| 2 | **Cảm biến mưa** | AO (Analog) | `GPIO 35` (D35) | Lỗ b32 bo phải | Đo cường độ mưa qua ADC – Input-only |
| 3 | **Servo SG90** | PWM (Dây cam) | `GPIO 27` (D27) | Lỗ g35 bo trái | Điều khiển van xả lũ (0°, 90°, 180°) |
| 4 | **Relay 1 kênh** | IN | `GPIO 23` (D23) | Lỗ b37 bo phải | Đóng/ngắt máy bơm 5V – **Active LOW** |
| 5 | **LED Đỏ** (Nguy cấp) | Anode (+) | `GPIO 18` (D18) | Lỗ b39 bo phải | Báo CRITICAL / DANGER – qua trở 220Ω |
| 6 | **LED Vàng** (Cảnh báo) | Anode (+) | `GPIO 19` (D19) | Lỗ b38 bo phải | Báo WARNING – qua trở 220Ω |
| 7 | **LED Xanh** (An toàn) | Anode (+) | `GPIO 21` (D21) | Lỗ b36 bo phải | Báo NORMAL – qua trở 220Ω |
| 8 | **Buzzer 5V** | Cực (+) | `GPIO 4` (D4) | Lỗ b34 bo phải | Còi cảnh báo âm thanh đa cấp độ |
| – | **Nút điều khiển** | *Ảo (Web)* | *Giao diện Web* | – | **Điều khiển qua Web Dashboard** (không dùng nút vật lý) |

### 2. Danh sách linh kiện phần cứng tổng hợp
| STT | Linh kiện | Mô tả / Chân ESP32 |
| :-: | :--- | :--- |
| 1 | **ESP32 DevKit V1** | Vi điều khiển trung tâm (tích hợp Wi-Fi & Web Server) |
| 2 | **HC-SR04** | Đo khoảng cách mực nước (`TRIG: GPIO 13`, `ECHO: GPIO 12`), dải đo: 50cm (0% - cạn) đến 5cm (100% - đầy tràn) |
| 3 | **Cảm biến mưa** | Phát hiện và đo cường độ mưa (`DO: GPIO 34`, `AO: GPIO 35` – cả 2 chân Input-only) |
| 4 | **Servo SG90** | Điều khiển góc mở van xả 0° – 90° – 180° (`PWM: GPIO 27`) |
| 5 | **Relay 1 kênh 5V** | Điều khiển bật/tắt máy bơm mini (`IN: GPIO 23` – **Active LOW**) |
| 6 | **Buzzer 5V** | Còi báo động đa cấp độ (`SIG: GPIO 4`) |
| 7 | **Cụm 3 LED + Điện trở** | Xanh (`GPIO 21`), Vàng (`GPIO 19`), Đỏ (`GPIO 18`) kèm trở 220Ω |
| 8 | **Web Dashboard Controls** | Hệ thống nút bấm điều khiển ảo trên trình duyệt (chuyển Mode, Bật/Tắt Bơm, Đổi góc Van) |

---

## 🚦 Các Trạng Thái Vận Hành & Ngưỡng Kích Hoạt
Hệ thống sử dụng cảm biến siêu âm với **khoảng đo từ 50cm (đáy hồ/cạn hoàn toàn - 0%) đến 5cm (mặt hồ đầy tràn - 100%)**, dải chênh lệch $45\text{ cm}$.

Áp dụng thuật toán **FSM & Hysteresis** chống dao động bật/tắt thiết bị với hệ thống cảnh báo đa tầng:
- **🟢 NORMAL (0 – 20% | Khoảng cách 50cm – 41cm)**: Mực nước an toàn. LED xanh sáng, Bơm OFF, Van đóng 0%, Còi OFF (yên lặng).
- **🟡 WARNING (21 – 40% | Khoảng cách 40.5cm – 32cm)**: Nước bắt đầu dâng. LED vàng sáng, **Còi báo nhẹ (tiếng bíp ngắn ngắt quãng thưa)** nhắc nhở kỹ thuật viên.
- **🔴 DANGER (41 – 70% | Khoảng cách 31.5cm – 18.5cm)**: Nguy cơ ngập. LED đỏ sáng, Bơm ON, Van mở 50% (90°), **Còi báo dồn dập (nhịp bíp nhanh)** cảnh báo nguy hiểm.
- **🚨 CRITICAL (71 – 100% | Khoảng cách 18cm – 5cm)**: Ngập nghiêm trọng. LED đỏ nhấp nháy dồn dập, **Còi hú liên tục không ngắt**, Bơm ON, Van mở thoát lũ tối đa 100% (180°).
- **Hysteresis khi nước rút**: Khi mực nước giảm, Bơm và Van vẫn duy trì thoát nước cho đến khi mực nước rút hẳn xuống dưới **40% (khoảng cách > 32cm)** mới ngắt Bơm đóng Van, và giảm sâu dưới **20% (khoảng cách > 41cm)** mới trở lại NORMAL.

---

## 🌐 Giám Sát & Điều Khiển Từ Xa (Web Dashboard)
- Tích hợp **Web Server** trên ESP32 (cổng 80).
- Giao diện Dashboard Dark Glassmorphism theo dõi:
  - Thanh đo mực nước hồ thu (%) thời gian thực.
  - Trạng thái thời tiết / cảm biến mưa.
  - Trạng thái máy bơm, góc mở van, còi hú.
  - Chuyển đổi linh hoạt giữa chế độ **AUTO** và **MANUAL**.
  - Can thiệp điều khiển thủ công Bơm và Van trực tiếp qua các nút bấm trên giao diện Web Dashboard (chuyển Mode AUTO/MANUAL, Bật/Tắt Bơm, mở Van 0% - 50% - 100%). Không phụ thuộc vào nút nhấn cơ học giúp tăng độ bền chống ẩm ướt trong môi trường ngập lụt.
- 👉 Chi tiết kiến trúc và các bước thiết lập Wi-Fi / Web Server xem tại: [WEB_DASHBOARD_SETUP_GUIDE.md](WEB_DASHBOARD_SETUP_GUIDE.md).

---

## 🚀 Hướng Dẫn Chạy Giả Lập Wokwi
1. Cài đặt extension **Wokwi for VS Code** và **PlatformIO IDE**.
2. Biên dịch firmware bằng PlatformIO:
   ```bash
   pio run
   ```
   *(hoặc nhấn tổ hợp phím `Ctrl + Shift + B`)*
3. Mở file `diagram.json` và nhấn nút **Start Simulation** (hoặc nhấn `F1` chọn `Wokwi: Start Simulator`).

👉 Xem hướng dẫn chi tiết từng bước và bảng lệnh tại file: [SIMULATION_GUIDE.md](SIMULATION_GUIDE.md).
