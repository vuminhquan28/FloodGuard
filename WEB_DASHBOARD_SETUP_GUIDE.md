# 🌐 ESP32 Wi-Fi & Web Dashboard Setup Guide

Tài liệu này cung cấp hướng dẫn toàn diện về kiến trúc, cấu hình Wi-Fi và phương thức thiết lập **Web Dashboard thời gian thực** trên vi điều khiển **ESP32** cho dự án **FloodGuard**.

---

## 🏗️ 1. Tổng Quan Kiến Trúc Hệ Thống (System Architecture)

Hệ thống hoạt động theo mô hình **Client - Server (HTTP REST API)** hoàn toàn độc lập, không phụ thuộc vào máy chủ ngoài:

```
+-------------------------------------------------------------+
|                      ESP32 Vi Điều Khiển                     |
|  [Cảm biến: HC-SR04, Mưa]  -->  [Thuật toán FSM & Hysteresis] |
|                                              |              |
|                                     [Thiết bị: Bơm, Van]    |
|                                                             |
|  +-------------------------------------------------------+  |
|  |           HTTP Web Server (Cổng 80 - WebServer.h)     |  |
|  |  * GET /            -> Trả về giao diện Dashboard     |  |
|  |  * GET /api/status  -> Trả về JSON dữ liệu đo đạc     |  |
|  |  * GET /api/control -> Tiếp nhận lệnh điều khiển      |  |
|  +-------------------------------------------------------+  |
+------------------------------▲------------------------------+
                               │ (Wi-Fi 802.11 b/g/n)
                               │
               +---------------+---------------+
               │                               │
       [Máy tính / Laptop]             [Điện thoại thông minh]
    (Trình duyệt: Chrome/Safari)    (Trình duyệt: Chrome/Safari)
```

* **Frontend:** Giao diện Dark Glassmorphism tối ưu hiển thị, lưu trực tiếp trong bộ nhớ Flash của ESP32 (`PROGMEM`), không cần thẻ nhớ SD.
* **Cơ chế cập nhật:** Trình duyệt sử dụng JavaScript (`fetch()` API) gửi request ngầm định kỳ mỗi **1 giây** để cập nhật dữ liệu mà không cần tải lại toàn bộ trang web (Single Page Application - SPA).

---

## 📶 2. Hai Chế Độ Hoạt Động Wi-Fi Trên ESP32

Tùy vào điều kiện triển khai thực tế, bạn có thể lựa chọn 1 trong 2 chế độ sau:

### Chế độ 1: Station Mode (STA) – Kết nối vào Router Wi-Fi *(Khuyên dùng)*
ESP32 kết nối vào mạng Wi-Fi sẵn có của gia đình hoặc phòng thí nghiệm.

* **Cấu hình trong code:**
  ```cpp
  #include <WiFi.h>

  const char* ssid     = "Ten_WiFi_Nha_Ban";
  const char* password = "Mat_Khau_WiFi";

  void setupWiFi() {
    Serial.print("Dang ket noi toi Wi-Fi: ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }

    Serial.println("\nWiFi da ket noi!");
    Serial.print("Dia chi IP truy cap Dashboard: http://");
    Serial.println(WiFi.localIP());
  }
  ```
* **Cách truy cập:**
  1. Đảm bảo điện thoại hoặc máy tính **kết nối cùng mạng Wi-Fi** với ESP32.
  2. Mở trình duyệt web (Chrome, Edge, Safari) và gõ địa chỉ IP hiển thị trên Serial Monitor (ví dụ: `http://192.168.1.150`).

---

### Chế độ 2: Soft Access Point Mode (SoftAP) – ESP32 tự phát Wi-Fi
Phù hợp khi triển khai ngoài hiện trường không có sóng Wi-Fi hoặc trạm phát mạng.

* **Cấu hình trong code:**
  ```cpp
  void setupSoftAP() {
    const char* ap_ssid = "FloodGuard_AP";
    const char* ap_pass = "12345678"; // Tối thiểu 8 ký tự

    WiFi.softAP(ap_ssid, ap_pass);
    Serial.println("ESP32 da phat mang Wi-Fi rieng!");
    Serial.print("Dia chi IP mac dinh: http://");
    Serial.println(WiFi.softAPIP()); // Thuong la http://192.168.4.1
  }
  ```
* **Cách truy cập:**
  1. Trên điện thoại/máy tính, tìm và kết nối vào mạng Wi-Fi tên **FloodGuard_AP** với mật khẩu `12345678`.
  2. Mở trình duyệt và truy cập vào địa chỉ: `http://192.168.4.1`.

---

## 💻 3. Cấu Trúc Mã Nguồn Web Server (Cổng 80)

Mã nguồn trong [src/main_hardware.cpp](src/main_hardware.cpp) và [src/main_wokwi.cpp](src/main_wokwi.cpp) đã được lập trình sẵn gồm 4 phần:

### 1. Khai báo thư viện và khởi tạo
```cpp
#include <WiFi.h>
#include <WebServer.h>

WebServer server(80);
```

### 2. Định tuyến API (Routing Endpoints)
Trong hàm `setup()`:
```cpp
// 1. Phục vụ giao diện HTML
server.on("/", handleRoot);

// 2. API trả về trạng thái JSON thời gian thực
server.on("/api/status", handleStatusApi);

// 3. API nhận lệnh điều khiển từ nút bấm trên Web
server.on("/api/control", handleControlApi);

server.begin();
```

### 3. Logic xử lý API
* **Endpoint `/api/status`:** Trả về chuỗi JSON chứa toàn bộ tham số (dải đo $50\text{cm} - 5\text{cm}$):
  ```json
  {
    "water": 45,
    "distance": 29.8,
    "rain": false,
    "rain_adc": 820,
    "state": "DANGER",
    "mode": "AUTO",
    "pump": true,
    "valve": 50,
    "buzzer": false
  }
  ```
* **Endpoint `/api/control?action={lenh}`:**
  * `mode_toggle`: Chuyển đổi giữa `AUTO` và `MANUAL`.
  * `pump_toggle`: Bật / Tắt máy bơm khi ở chế độ `MANUAL`.
  * `valve_0`, `valve_50`, `valve_100`: Thay đổi khẩu độ van xả (0°, 90°, 180°).

### 4. Lắng nghe liên tục trong `loop()`
```cpp
void loop() {
  server.handleClient(); // Bắt buộc: Xử lý request từ trình duyệt
  
  // Các tác vụ non-blocking khác...
}
```

---

## 🧪 4. Thiết Lập & Truy Cập Dashboard Trong Giả Lập Wokwi

Trong môi trường mô phỏng ảo Wokwi:

1. **Kết nối mạng ảo:** Wokwi cung cấp mạng Wi-Fi ảo với SSID:
   ```cpp
   WiFi.begin("Wokwi-GUEST", "");
   ```
2. **Cầu nối mạng Wokwi IoT Gateway (Dành cho VS Code):**
   * Do ESP32 chạy mô phỏng bên trong sandbox của VS Code, để trình duyệt trên máy tính thật (Chrome) giao tiếp được với IP ảo của ESP32, Wokwi sử dụng công cụ **Wokwi IoT Gateway**.
   * Chi tiết hướng dẫn tải và chạy Gateway: xem tại [docs.wokwi.com/guides/esp32-wifi](https://docs.wokwi.com/guides/esp32-wifi).
3. **Chạy trực tiếp trên Web Wokwi.com:**
   * Nếu nạp project lên trang web [wokwi.com](https://wokwi.com), Wokwi hỗ trợ đường link chuyển tiếp trực tiếp vào Web Server của ESP32 chỉ bằng 1 cú nhấp chuột.

---

## 🌍 5. Mở Rộng: Điều Khiển Từ Xa Qua Internet (Ngoài Mạng LAN)

Mạng Wi-Fi nội bộ (LAN) chỉ cho phép truy cập khi ở trong cùng tầm phát sóng của Router. Nếu muốn giám sát khi ra ngoài đường bằng mạng 4G/5G, có 2 giải pháp tiêu chuẩn:

### Giải pháp 1: Sử dụng giao thức MQTT & Cloud IoT Platform *(Khuyên dùng cho đồ án lớn)*
* ESP32 đóng vai trò là MQTT Client, gửi dữ liệu lên Cloud Broker miễn phí (HiveMQ Cloud, EMQX, Adafruit IO hoặc Blynk IoT).
* Người dùng mở ứng dụng di động hoặc Web Dashboard kết nối vào Broker để theo dõi và điều khiển từ bất kỳ đâu trên thế giới.

### Giải pháp 2: Sử dụng đường hầm an toàn (Cloudflare Tunnel / Ngrok)
* Dùng một máy tính hoặc Raspberry Pi trong nhà chạy Ngrok / Cloudflare Tunnel để trỏ một tên miền công khai (ví dụ: `https://floodguard.myproject.dev`) về địa chỉ IP cục bộ của ESP32.

---

## ⚡ 6. Lưu Ý Kỹ Thuật Quan Trọng
1. **Không dùng `delay()` trong `loop()`:** Các hàm `delay()` dài sẽ làm nghẽn tiến trình của Web Server, dẫn đến việc trình duyệt web bị xoay tròn hoặc mất kết nối (`Connection Timed Out`). Luôn sử dụng kỹ thuật non-blocking với `millis()`.
2. **Tên miền cục bộ (mDNS):** Bạn có thể tích hợp thư viện `ESPmDNS.h` để truy cập dashboard bằng đường dẫn thân thiện `http://floodguard.local` thay vì phải nhớ dãy số IP.

