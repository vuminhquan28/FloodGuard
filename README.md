# 🌊 FloodGuard - Hệ Thống Giám Sát & Chống Ngập Thông Minh

Hệ thống IoT ứng dụng **ESP32** kết hợp cảm biến siêu âm HC-SR04, cảm biến mưa, màn hình LCD 1602 I2C, động cơ Servo điều khiển van xả, Relay điều khiển máy bơm, còi cảnh báo và hệ thống Web Server giám sát qua Wi-Fi thời gian thực.

---

## 🛠️ Danh Sách Linh Kiện (Hardware & Simulation)
| STT | Linh kiện | Mô tả / Chân ESP32 |
| :-: | :--- | :--- |
| 1 | **ESP32 DevKit V1** | Vi điều khiển trung tâm (tích hợp Wi-Fi) |
| 2 | **HC-SR04** | Đo khoảng cách mực nước (`TRIG: 18`, `ECHO: 5`) |
| 3 | **Cảm biến mưa** | Đo độ ẩm / nước mưa analog (`ADC: 34`) |
| 4 | **LCD 1602 (I2C)** | Hiển thị thông số tại chỗ (`SDA: 21`, `SCL: 22`) |
| 5 | **Servo SG90** | Điều khiển góc mở van xả 0° – 90° – 180° (`PWM: 13`) |
| 6 | **Relay 1 kênh 5V** | Điều khiển bật/tắt máy bơm mini (`IN: 23`) |
| 7 | **Buzzer 5V** | Còi báo động mức nguy cấp (`SIG: 19`) |
| 8 | **Cụm 3 LED** | Xanh (`GPIO 25`), Vàng (`GPIO 26`), Đỏ (`GPIO 27`) |
| 9 | **3 Nút nhấn** | Mode (`GPIO 32`), Pump (`GPIO 33`), Valve (`GPIO 14`) |

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
  - Can thiệp điều khiển thủ công Bơm và Van trực tiếp qua trình duyệt web hoặc nút nhấn trên mạch.

---

## 🚀 Hướng Dẫn Chạy Giả Lập Wokwi
1. Cài đặt extension **Wokwi for VS Code**.
2. Biên dịch firmware bằng PlatformIO:
   ```bash
   pio run
   ```
3. Mở file `diagram.json` và nhấn nút **Start Simulation** (hoặc nhấn `F1` chọn `Wokwi: Start Simulator`).
