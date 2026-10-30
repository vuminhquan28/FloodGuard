# 🚀 Hướng Dẫn Biên Dịch & Chạy Giả Lập Wokwi - Dự Án FloodGuard

Tài liệu này hướng dẫn chi tiết cách biên dịch mã nguồn và khởi chạy mô phỏng hệ thống chống ngập tự động **FloodGuard (ESP32)** bằng **Wokwi Simulator** ngay trên VS Code / Antigravity IDE.

---

## 📦 1. Các Extension Cần Thiết
Đảm bảo bạn đã cài đặt các extension sau trong VS Code :

1. **Wokwi Simulator** (`wokwi.wokwi-vscode`): Trình giả lập phần cứng ESP32 và các linh kiện IoT.
2. **PlatformIO IDE** (`platformio.platformio-ide`): Môi trường quản lý thư viện và biên dịch mã nguồn C/C++.
3. **C/C++** (`ms-vscode.cpptools`): Hỗ trợ gợi ý code (IntelliSense) và kiểm tra lỗi cú pháp.

---

## ⚡ 2. Các Bước Thực Hiện Chi Tiết

### Bước 1: Biên dịch mã nguồn (Build Firmware)
Mỗi khi bạn tạo mới hoặc chỉnh sửa mã nguồn mô phỏng trong `src/main_wokwi.cpp`, bạn cần biên dịch để tạo file firmware mới:

* **Cách 1 (Dùng Terminal):**
  Mở terminal trong VS Code (nhấn phím tắt `` Ctrl + ` ``) và chạy lệnh:
  ```powershell
  pio run
  ```
  *(Khi xuất hiện chữ `[SUCCESS]`, firmware đã được xuất vào thư mục `.pio/build/esp32dev/firmware.bin`).*

* **Cách 2 (Dùng phím tắt nhanh):**
  Nhấn tổ hợp phím **`Ctrl + Shift + B`** $\rightarrow$ Chọn **PlatformIO: Build**.

---

### Bước 2: Khởi động giả lập Wokwi
Sau khi biên dịch thành công:

* **Cách 1:** 
  1. Mở file [diagram.json](diagram.json).
  2. Nhấp vào nút **Start Simulation** (biểu tượng nút Play màu xanh lá) nằm ở phía trên giao diện sơ đồ mạch.

* **Cách 2:**
  1. Nhấn phím **`F1`** (hoặc `Ctrl + Shift + P`) để mở Command Palette.
  2. Gõ tìm: `Wokwi: Start Simulator` và nhấn **Enter**.

---

### Bước 3: Tương tác và theo dõi hệ thống
* **Serial Monitor:** Cửa sổ Terminal sẽ tự động hiển thị log từ lệnh `Serial.print()` của ESP32 với tốc độ baud `115200`.
* **Cảm biến siêu âm (HC-SR04):** Nhấp chuột vào cảm biến HC-SR04 trên sơ đồ mô phỏng để kéo thanh trượt thay đổi khoảng cách mực nước trong dải thiết kế **50cm (0% - cạn hoàn toàn)** đến **5cm (100% - đầy tràn)**.
* **Cảm biến mưa (Rain Potentiometer):** Xoay núm biến trở để giả lập độ ẩm/nước mưa.
* **Quan sát thiết bị chấp hành:**
  * **Đèn LED (Xanh / Vàng / Đỏ):** Hiển thị các mức trạng thái nước an toàn, cảnh báo, nguy cấp.
  * **Còi Buzzer đa cấp độ:**
    * *Mức NORMAL:* Yên lặng (tắt).
    * *Mức WARNING:* Còi báo nhẹ (tiếng bíp ngắn thưa ngắt quãng).
    * *Mức DANGER:* Còi báo dồn dập (nhịp bíp nhanh liên hồi).
    * *Mức CRITICAL:* Còi hú liên tục không ngắt báo động khẩn cấp.
  * **Động cơ Servo:** Quay góc 0° – 90° – 180° tương ứng các mức độ mở van xả.
  * **Relay:** Đóng/ngắt để kích hoạt máy bơm nước.
* **Điều khiển thủ công qua Web Dashboard:** Toàn bộ việc chuyển đổi chế độ (AUTO/MANUAL), bật/tắt Bơm và xoay góc mở Van xả được thực hiện trực tiếp thông qua hệ thống nút bấm ảo trên giao diện Web Dashboard (địa chỉ IP hiển thị trên Serial Monitor, hoặc endpoint `/api/control`). Hệ thống không còn sử dụng nút bấm cơ học giúp tối giản phần cứng và chống hư hỏng trong môi trường nước.

---

## 🛠️ 3. Bảng Lệnh Terminal PlatformIO Thường Dùng

| Lệnh | Ý nghĩa |
| :--- | :--- |
| `pio run` (hoặc `pio run -e esp32dev`) | Biên dịch code mô phỏng `main_wokwi.cpp` cho Wokwi |
| `pio run -e hardware` | Biên dịch code phần cứng `main_hardware.cpp` (SoftAP) |
| `pio run -e hardware -t upload` | Nạp code `main_hardware.cpp` vào board ESP32 thật qua cáp USB |
| `pio run -t clean` | Dọn dẹp các file cache đã biên dịch |
| `pio device monitor` | Mở màn hình đọc Serial port khi cắm ESP32 thật vào máy |

---

## ❓ 4. Xử Lý Sự Cố Thường Gặp (Troubleshooting)

### 1. Terminal báo lỗi: `pio: The term 'pio' is not recognized...`
* **Nguyên nhân:** Đường dẫn PlatformIO chưa được nạp vào phiên làm việc hiện tại của terminal.
* **Khắc phục:** 
  * Tắt terminal hiện tại và mở một terminal PowerShell mới (nhấn dấu `+` ở thanh Terminal).
  * Đường dẫn `C:\Users\thuyb\.platformio\penv\Scripts` đã được lưu trong Windows User PATH.

### 2. Sửa code trong `main.cpp` nhưng mô phỏng Wokwi không có gì thay đổi
* **Nguyên nhân:** Bạn chưa biên dịch lại firmware trước khi chạy mô phỏng.
* **Khắc phục:**
  1. Dừng mô phỏng (nhấn nút Stop hoặc `F1` $\rightarrow$ `Wokwi: Stop Simulator`).
  2. Chạy `pio run` (hoặc `Ctrl + Shift + B`).
  3. Khởi động lại mô phỏng Wokwi.

### 3. Wokwi yêu cầu License Token
* File token kích hoạt Wokwi đã được lưu sẵn tại: `C:\Users\thuyb\.wokwi\user.tok`. Nếu extension yêu cầu kích hoạt lại, bạn chỉ cần nhấn vào thông báo `Get License` hoặc đăng nhập bằng tài khoản Wokwi của bạn.

