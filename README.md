# 🌊 FloodGuard - Hệ Thống Giám Sát & Chống Ngập Thông Minh

Hệ thống IoT ứng dụng **ESP32** kết hợp cảm biến siêu âm HC-SR04, cảm biến mưa, động cơ Servo điều khiển van xả, Relay điều khiển máy bơm, còi cảnh báo và hệ thống Web Server giám sát qua Wi-Fi thời gian thực (hiển thị trực tiếp trên máy tính / điện thoại).

---

## 🛠️ Danh Sách Linh Kiện & Bảng Phân Công Chân (GPIO Mapping)

### 1. Bảng phân công chân phần cứng (GPIO Mapping)
| Thiết bị / Module | Chân tín hiệu | Vị trí chân GPIO trên ESP32 | Ghi chú |
| :--- | :--- | :--- | :--- |
| **LED Xanh** (Mức an toàn) | Anode (+) | `GPIO 25` | Qua trở hạn dòng 220Ω |
| **LED Vàng** (Cảnh báo vừa) | Anode (+) | `GPIO 26` | Qua trở hạn dòng 220Ω |
| **LED Đỏ** (Cảnh báo nguy cấp) | Anode (+) | `GPIO 27` | Qua trở hạn dòng 220Ω |
| **Còi Buzzer** | (+) | `GPIO 19` | Active Buzzer cảnh báo khẩn cấp |
| **HC-SR04 (Trig)** | Trig | `GPIO 18` | Phát xung kích hoạt |
| **HC-SR04 (Echo)** | Echo | `GPIO 5` | Nhận xung phản hồi |
| **Cảm biến mưa (Potentiometer)** | Analog Out | `GPIO 34` | Đo cường độ mưa / độ ẩm hồ thu |
| **Servo SG90** | PWM | `GPIO 13` | Điều khiển góc mở van xả lũ (0° – 90° – 180°) |
| **Relay 1 kênh 5V** | IN | `GPIO 23` | Kích hoạt đóng/ngắt máy bơm mini |
| **Nút điều khiển (Mode, Pump, Valve)** | *Ảo (Web)* | *Giao diện Web* | **Điều khiển hoàn toàn qua Web Dashboard** (không dùng nút vật lý) |

### 2. Danh sách linh kiện phần cứng tổng hợp
| STT | Linh kiện | Mô tả / Chân ESP32 |
| :-: | :--- | :--- |
| 1 | **ESP32 DevKit V1** | Vi điều khiển trung tâm (tích hợp Wi-Fi & Web Server) |
| 2 | **HC-SR04** | Đo khoảng cách mực nước (`TRIG: 18`, `ECHO: 5`) |
| 3 | **Cảm biến mưa / Chiết áp** | Giả lập lượng mưa / độ ẩm (`ADC: GPIO 34`) |
| 4 | **Servo SG90** | Điều khiển góc mở van xả 0° – 90° – 180° (`PWM: 13`) |
| 5 | **Relay 1 kênh 5V** | Điều khiển bật/tắt máy bơm mini (`IN: 23`) |
| 6 | **Buzzer 5V** | Còi báo động mức nguy cấp (`SIG: 19` - Active Buzzer) |
| 7 | **Cụm 3 LED + Điện trở** | Xanh (`GPIO 25`), Vàng (`GPIO 26`), Đỏ (`GPIO 27`) kèm trở 220Ω |
| 8 | **Web Dashboard Controls** | Hệ thống nút bấm điều khiển ảo trên trình duyệt (chuyển Mode, Bật/Tắt Bơm, Đổi góc Van) |

---

## 🚦 Các Trạng Thái Vận Hành & Ngưỡng Kích Hoạt
Hệ thống áp dụng thuật toán **FSM & Hysteresis** chống dao động bật/tắt thiết bị:
- **🟢 NORMAL (0 – 20%)**: Mực nước an toàn. LED xanh sáng, Bơm OFF, Van đóng 0%, Còi OFF.
- **🟡 WARNING (21 – 40%)**: Nước bắt đầu dâng. LED vàng sáng, cảnh báo sớm.
- **🔴 DANGER (41 – 70%)**: Nguy cơ ngập. LED đỏ sáng, Bơm ON, Van mở 50% (90°).
- **🚨 CRITICAL (71 – 100%)**: Ngập nghiêm trọng. LED đỏ nhấp nháy, Còi hú dồn dập, Bơm ON, Van mở 100% (180°).
- **Hysteresis khi nước rút**: Khi mực nước giảm, Bơm và Van vẫn duy trì thoát nước cho đến khi mực nước rút hẳn xuống dưới **40%** mới ngắt Bơm đóng Van, và giảm dưới **20%** mới trở lại NORMAL.

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
