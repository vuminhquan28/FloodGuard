# 🌐 Hướng Dẫn Sử Dụng & Kiểm Thử Web Dashboard FloodGuard

Tài liệu này cung cấp hướng dẫn thực hành chi tiết từ A-Z về:
1. **Kiểm thử giao diện Web Dashboard Offline ngay trên máy tính** (không cần phần cứng).
2. **Cách kết nối bo mạch ESP32 và nạp Firmware**.
3. **Cách kết nối mạng Wi-Fi và truy cập Web Dashboard** từ điện thoại hoặc máy tính.
4. **Quy trình kiểm thử từng tính năng giám sát và điều khiển trên Web**.
5. **Khắc phục sự cố thường gặp (Troubleshooting)**.

---

## 📑 Mục Lục
- [1. Tổng Quan Kiến Trúc Web Dashboard](#1-tổng-quan-kiến-trúc-web-dashboard)
- [2. Cách 1: Test Nhanh Giao Diện Web Offline (Không cần phần cứng)](#2-cách-1-test-nhanh-giao-diện-web-offline-không-cần-phần-cứng)
- [3. Cách 2: Kết Nối Phần Cứng & Nạp Code Lên ESP32](#3-cách-2-kết-nối-phần-cứng--nạp-code-lên-esp32)
- [4. Kết Nối Wi-Fi & Truy Cập Web Dashboard Thực Tế](#4-kết-nối-wi-fi--truy-cập-web-dashboard-thực-tế)
- [5. Quy Trình Kiểm Thử Chi Tiết Từng Chức Năng Của Web](#5-quy-trình-kiểm-thử-chi-tiết-từng-chức-năng-của-web)
- [6. Bảng Đặc Tả Lệnh REST API Cho Web](#6-bảng-đặc-tả-lệnh-rest-api-cho-web)
- [7. Xử Lý Các Sự Cố Thường Gặp (Troubleshooting)](#7-xử-lý-các-sự-cố-thường-gặp-troubleshooting)

---

## 🏗️ 1. Tổng Quan Kiến Trúc Web Dashboard

Hệ thống hoạt động theo mô hình **Client - Server (HTTP REST API)** hoàn toàn độc lập, sử dụng chế độ phát Wi-Fi nội bộ (**SoftAP Mode**), không phụ thuộc vào Internet hay Router gia đình:

```
+-----------------------------------------------------------------+
|                      ESP32 Vi Điều Khiển                        |
|  [HC-SR04, Cảm biến Mưa]  ──►  [Thuật toán FSM & Hysteresis]    |
|                                            │                    |
|                                   [Relay Bơm, Servo Van]        |
|                                                                 |
|  +-----------------------------------------------------------+  |
|  |           HTTP Web Server (Cổng 80 - WebServer.h)         |  |
|  |  * GET /            -> Phục vụ trang HTML/CSS/JS          |  |
|  |  * GET /api/status  -> Trả về JSON telemetry thời gian thực|  |
|  |  * GET /api/control -> Tiếp nhận lệnh điều khiển cưỡng chế |  |
|  +-----------------------------------------------------------+  |
+--------------------------------▲--------------------------------+
                                 │ (Sóng Wi-Fi: FloodGuard_AP)
                                 │
                 +---------------+---------------+
                 │                               │
         [Điện thoại thông minh]         [Máy tính / Laptop]
          (Chrome, Safari, Edge)        (Chrome, Edge, Firefox)
```

* **Frontend:** Giao diện **Dark Glassmorphism** hiện đại, responsive co giãn tự động trên mọi kích cỡ màn hình.
* **Bộ nhớ:** Toàn bộ trang web được nén lưu trong bộ nhớ Flash `PROGMEM` của ESP32 (tiêu thụ $0\,\text{bytes}$ RAM khi ở trạng thái nghỉ).
* **Cơ chế truyền thông:** Trình duyệt JavaScript tự động gửi lệnh ngầm `fetch('/api/status')` mỗi **$1000\,\text{ms}$** để cập nhật thông số theo thời gian thực (Single Page Application - SPA).

---

## 🖥️ 2. Cách 1: Test Nhanh Giao Diện Web Offline (Không Cần Phần Cứng)

Nếu bạn chưa có sẵn mạch ESP32 bên cạnh hoặc muốn kiểm tra ngay giao diện hiển thị, các hiệu ứng đổi màu, trạng thái nút bấm:

### Bước 1: Mở tệp giao diện xem trước
1. Điều hướng đến thư mục dự án: `d:\1. project\FloodGuard\`.
2. Tìm tệp **`preview_dashboard.html`**.
3. Nhấp đúp chuột để mở trực tiếp trên trình duyệt web bất kỳ (**Google Chrome**, **Microsoft Edge**, hoặc **Firefox**).

### Bước 2: Thao tác với thanh công cụ mô phỏng (Preview Toolbar)
Ở góc dưới cùng màn hình có thanh công cụ màu đen viền xanh dương giúp bạn giả lập mọi tình huống cảm biến:

| Công cụ mô phỏng | Cách thao tác | Kết quả hiển thị kiểm tra |
| :--- | :--- | :--- |
| **Thanh kéo Mực Nước** | Kéo thanh trượt từ $0\%$ đến $100\%$ | • $0 - 20\%$: Thanh đo màu xanh lá, nhãn **NORMAL**.<br>• $21 - 40\%$: Thanh đo màu vàng, nhãn **WARNING**.<br>• $41 - 70\%$: Thanh đo màu đỏ, nhãn **DANGER**, Bơm tự BẬT, Van mở $50\%$.<br>• $71 - 100\%$: Thanh đo đỏ rực, nhãn **CRITICAL** (chớp nháy), Van mở toang $100\%$, Còi hú liên tục. |
| **Hộp chọn Cấp Độ Mưa** | Chọn: Khô ráo, Mưa nhỏ, Mưa to, Ngập nước | Thẻ thời tiết cập nhật giá trị ADC và cảnh báo cấp độ mưa tức thời. |
| **Nút đổi chế độ** | Bấm `Đổi Chế Độ (AUTO / MANUAL)` | Chuyển đổi qua lại giữa chế độ tự trị FSM và can thiệp thủ công. |
| **Cụm nút điều khiển** | Bấm `Bật/Tắt Bơm`, `Van 0%`, `Van 50%`, `Van 100%` | Kiểm tra phản hồi góc quay van và trạng thái máy bơm trên thẻ thiết bị. |

---

## 🔌 3. Cách 2: Kết Nối Phần Cứng & Nạp Code Lên ESP32

### Bước 1: Kết nối dây phần cứng
1. Cắm bo **ESP32 Dev Module** vào cổng USB máy tính qua cáp truyền dữ liệu (chú ý dùng cáp có dây Data, không dùng cáp chỉ có sạc).
2. Kiểm tra sơ đồ chân kết nối:
   * **HC-SR04:** Trig $\rightarrow$ `GPIO 13`, Echo $\rightarrow$ `GPIO 12`.
   * **Cảm biến Mưa FC-37:** DO $\rightarrow$ `GPIO 34`, AO $\rightarrow$ `GPIO 35`.
   * **Relay Máy Bơm 5V:** IN $\rightarrow$ `GPIO 23` (Kỹ thuật High-Z, Active LOW).
   * **Servo SG90 Van Xả:** PWM $\rightarrow$ `GPIO 27`.
   * **Còi Active Buzzer:** Tín hiệu $\rightarrow$ `GPIO 4`.
   * **3 Đèn LED:** Xanh $\rightarrow$ `GPIO 21`, Vàng $\rightarrow$ `GPIO 19`, Đỏ $\rightarrow$ `GPIO 18`.

### Bước 2: Nạp Firmware lên ESP32

Bạn có thể lựa chọn 1 trong 2 cách nạp sau:

#### Cách 2.1: Sử dụng PlatformIO (Khuyên dùng)
Mở cửa sổ PowerShell hoặc Terminal tại thư mục `d:\1. project\FloodGuard\` và chạy lệnh:
```powershell
# Biên dịch và nạp trực tiếp qua cổng COM tự động nhận diện:
pio run -e hardware -t upload

# Mở màn hình theo dõi Serial Monitor (tốc độ 115200):
pio device monitor -b 115200
```

#### Cách 2.2: Sử dụng Arduino IDE
1. Khởi động phần mềm **Arduino IDE**.
2. Mở file: `d:\1. project\FloodGuard\main\main\main.ino`.
3. Vào menu **Tools** $\rightarrow$ **Board** $\rightarrow$ Chọn **ESP32 Dev Module**.
4. Vào menu **Tools** $\rightarrow$ **Port** $\rightarrow$ Chọn đúng cổng COM của bo ESP32 (ví dụ `COM3`, `COM4`...).
5. Nhấn nút **Upload** (Mũi tên chỉ sang phải `➔`) và chờ quá trình nạp đạt $100\%$.
6. Mở **Serial Monitor** (Ctrl + Shift + M), chỉnh baudrate góc dưới sang **115200 baud**.

### Bước 3: Xác nhận thông báo khởi động trên Serial Monitor
Khi ESP32 khởi động thành công, Serial Monitor sẽ in ra nội dung như sau:
```
==========================================
FLOODGUARD - CHE DO ACCESS POINT (HARDWARE)
==========================================
[Wi-Fi] ESP32 da phat mang Wi-Fi thanh cong!
[Wi-Fi] Ten mang (SSID): FloodGuard_AP
[Wi-Fi] Mat khau (PASS) : 12345678
[Wi-Fi] Dia chi IP Web : http://192.168.4.1
[mDNS] Truy cap bang ten mien: http://floodguard.local
[HTTP] Web Server da san sang tren cong 80.
==========================================
```

---

## 📱 4. Kết Nối Wi-Fi & Truy Cập Web Dashboard Thực Tế

Sau khi bo mạch đã nạp firmware và cấp nguồn thành công:

### Bước 1: Kết nối vào mạng Wi-Fi của ESP32
1. Lấy **Điện thoại thông minh** (iPhone, Android) hoặc **Laptop**.
2. Mở phần **Cài đặt Wi-Fi** trên máy.
3. Tìm và chọn mạng Wi-Fi có tên:
   * **Tên mạng (SSID):** `FloodGuard_AP`
   * **Mật khẩu (Password):** `12345678`
4. ⚠️ **LƯU Ý QUAN TRỌNG:** 
   * Do đây là mạng Wi-Fi nội bộ không có Internet, điện thoại có thể hiện thông báo: *"Mạng Wi-Fi này không có kết nối Internet. Bạn có muốn giữ kết nối không?"*.
   * Hãy bấm chọn **"GIỮ KẾT NỐI" (Keep Connection / Stay Connected)**.
   * Nếu dùng điện thoại, nên **tạm tắt dữ liệu di động (4G/5G)** trong lúc test để trình duyệt không tự ý chuyển hướng ra ngoài Internet.

### Bước 2: Mở Web Dashboard trên trình duyệt
1. Mở trình duyệt web ưa thích (**Chrome**, **Safari**, hoặc **Edge**).
2. Nhập trực tiếp địa chỉ IP vào thanh URL:
   ```
   http://192.168.4.1
   ```
   *(Hoặc gõ: `http://floodguard.local` nếu thiết bị có hỗ trợ mDNS)*.
3. Nhấn **Enter / Đi tới**. Giao diện giám sát **FloodGuard Dashboard Dark Glassmorphism** sẽ xuất hiện ngay lập tức!

---

## 🧪 5. Quy Trình Kiểm Thử Chi Tiết Từng Chức Năng Của Web

Hãy thực hiện kiểm tra tuần tự 4 bài test dưới đây để xác nhận sự đồng bộ giữa Web và phần cứng:

### Bài Test 1: Giám sát đo đạc thời gian thực (Telemetry Loop)
1. Để cảm biến siêu âm tự do trong không khí.
2. Quan sát thẻ **"Mực Nước Hồ Thu"** trên Web Dashboard:
   * Cầm một tấm bìa hoặc lòng bàn tay di chuyển lại gần mặt cảm biến (từ $50\,\text{cm}$ lại gần $10\,\text{cm}$).
   * **Xác nhận:** Thông số khoảng cách $\text{cm}$ và thanh tiến trình phần trăm $\%$ trên màn hình web phải thay đổi nhảy số liên tục đều đặn mỗi **1 giây** mà không cần nhấn F5 tải lại trang.

### Bài Test 2: Thử nghiệm cảm biến mưa
1. Nhỏ 1–2 giọt nước lên tấm cảm biến mưa FC-37.
2. **Xác nhận trên Web:**
   * Thẻ thời tiết lập tức đổi từ `"KHONG MUA"` sang `"MUA NHO"` (màu xanh dương) hoặc `"MUA TO"` (màu cam).
   * Giá trị `rain_adc` tụt từ $\approx 3500$ xuống dưới $2800$.
   * Huy hiệu trạng thái đổi sang màu vàng **`WARNING`**.
   * Đèn LED Vàng trên mạch bật sáng.

### Bài Test 3: Can thiệp điều khiển thủ công (Manual Override)
1. Nhấp nút **`Đổi Chế Độ (AUTO / MANUAL)`**:
   * Huy hiệu chế độ trên web chuyển từ **`AUTO`** sang màu cam **`MANUAL`**.
2. **Thử điều khiển máy bơm:**
   * Nhấp nút **`Bật/Tắt Bơm (Manual)`**.
   * **Xác nhận:** Rơ-le trên mạch nhảy tiếng *"tách"*, đèn đỏ rơ-le sáng, máy bơm mini 5V bắt đầu chạy, dòng chữ trên web đổi sang **`ĐANG BẬT (ON)`** màu xanh lá.
   * Nhấp lại nút một lần nữa $\rightarrow$ Máy bơm tắt, dòng chữ đổi sang **`ĐÃ TẮT (OFF)`**.
3. **Thử điều khiển van xả nước (Servo SG90):**
   * Nhấp **`Van 50% (Mở Nửa)`** $\rightarrow$ Cánh van Servo quay sang góc $90^\circ$, web báo `50%`.
   * Nhấp **`Van 100% (Mở Hết)`** $\rightarrow$ Cánh van Servo quay sang góc $180^\circ$, web báo `100%`.
   * Nhấp **`Van 0% (Đóng)`** $\rightarrow$ Cánh van Servo quay gập về góc $0^\circ$, web báo `0%`.

### Bài Test 4: Chuyển lại chế độ Tự Động (AUTO)
1. Nhấp lại nút **`Đổi Chế Độ (AUTO / MANUAL)`**.
2. Huy hiệu chuyển lại thành màu xanh **`AUTO`**.
3. Bây giờ thử nhấp các nút Bơm hoặc Van $\rightarrow$ Hệ thống sẽ bảo vệ và không thực thi lệnh can thiệp nữa, toàn quyền điều khiển được giao lại cho thuật toán máy trạng thái FSM.

---

## 📡 6. Bảng Đặc Tả Lệnh REST API Cho Web

Các lập trình viên có thể dùng Postman, cURL hoặc ứng dụng di động bên ngoài để giao tiếp với ESP32 thông qua các endpoint sau:

| Endpoint | Method | Tham số (Query Param) | Mô tả chức năng | Kết quả phản hồi |
| :--- | :---: | :--- | :--- | :--- |
| **`/`** | `GET` | Không có | Tải toàn bộ giao diện Web Dashboard (HTML/CSS/JS) | Mã 200, chuỗi HTML |
| **`/api/status`** | `GET` | Không có | Lấy gói tin JSON đo đạc thời gian thực | Mã 200, chuỗi JSON |
| **`/api/control`** | `GET` | `action=mode_toggle` | Đảo trạng thái giữa AUTO và MANUAL | Mã 200, chuỗi `"OK"` |
| **`/api/control`** | `GET` | `action=pump_toggle` | Bật hoặc tắt máy bơm 5V (chỉ ở MANUAL) | Mã 200, chuỗi `"OK"` |
| **`/api/control`** | `GET` | `action=valve_0` | Xoay van Servo về $0^\circ$ (chỉ ở MANUAL) | Mã 200, chuỗi `"OK"` |
| **`/api/control`** | `GET` | `action=valve_50` | Xoay van Servo mở $90^\circ$ ($50\%$) | Mã 200, chuỗi `"OK"` |
| **`/api/control`** | `GET` | `action=valve_100` | Xoay van Servo mở tối đa $180^\circ$ ($100\%$) | Mã 200, chuỗi `"OK"` |

#### Cấu trúc chuỗi JSON trả về tại `/api/status`:
```json
{
  "water": 45,
  "distance": 29.8,
  "rain": true,
  "rain_adc": 1420,
  "state": "DANGER",
  "mode": "MANUAL",
  "pump": true,
  "valve": 50,
  "buzzer": "FAST"
}
```

---

## 🛠️ 7. Xử Lý Các Sự Cố Thường Gặp (Troubleshooting)

### Sự cố 1: Điện thoại kết nối Wi-Fi nhưng không mở được `192.168.4.1`
* **Nguyên nhân:** Điện thoại phát hiện Wi-Fi `FloodGuard_AP` không có mạng Internet nên tự động dùng mạng dữ liệu di động (4G/5G) để gửi request, dẫn tới không tìm thấy IP cục bộ của ESP32.
* **Cách khắc phục:** 
  1. Tắt hoàn toàn **Dữ liệu di động (4G/LTE/5G)** trên điện thoại.
  2. Ngắt kết nối Wi-Fi và kết nối lại vào `FloodGuard_AP`.
  3. Chọn xác nhận **"Giữ kết nối" / "Stay connected"** khi được hỏi.

### Sự cố 2: Không tìm thấy mạng Wi-Fi tên `FloodGuard_AP`
* **Nguyên nhân:** Bo mạch ESP32 chưa được cấp đủ nguồn hoặc đang bị kẹt trong vòng lặp boot.
* **Cách khắc phục:**
  1. Nhấn nút **EN / RESET** trên bo ESP32 để khởi động lại.
  2. Mở Serial Monitor xem có dòng chữ: `[Wi-Fi] ESP32 da phat mang Wi-Fi thanh cong!` hay không.
  3. Nếu mạch chớp đèn đỏ liên tục: Rút bớt tải nguồn ngoài (nguồn máy bơm 5V nên cắm riêng qua củ sạc USB để không làm sụt áp cổng USB máy tính).

### Sự cố 3: Bấm nút trên Web nhưng máy bơm và van không phản hồi
* **Nguyên nhân:** Hệ thống đang ở chế độ `AUTO` (Tự động) nên logic FSM từ chối lệnh can thiệp thủ công để đảm bảo an toàn.
* **Cách khắc phục:** Nhấp nút **`Đổi Chế Độ (AUTO / MANUAL)`** trước, đợi thẻ chế độ chuyển sang màu cam **`MANUAL`** rồi mới bấm nút Bơm và Van.

### Sự cố 4: Số đo mực nước hoặc góc van trên Web bị đứng hình, không nhảy số
* **Nguyên nhân:** Trình duyệt web bị mất kết nối ngầm với ESP32 hoặc CPU của ESP32 bị treo.
* **Cách khắc phục:**
  1. F5 tải lại trang web.
  2. Đảm bảo trong mã nguồn hàm `loop()` không chứa bất kỳ hàm `delay()` lớn nào chặn luồng `server.handleClient()`.

### Sự cố 5: Ở MANUAL, bấm nút trên Web thì đèn xanh Relay bật sáng nhưng Bơm không chạy và Van không đổi
Đây là hiện tượng rất phổ biến khi đấu nối thực tế:
* **Khẳng định kết nối Code & Vi điều khiển:** Đèn xanh trên Relay sáng chứng minh **ESP32, Web Server, lệnh API và chân GPIO 23 đã hoạt động hoàn hảo 100%**.
* **Nguyên nhân Máy Bơm không chạy (Lỗi mạch điện tiếp điểm khô):**
  * Module Relay 1 kênh là một **công tắc tiếp điểm khô (Dry Contact)**, các chân ốc `COM` và `NO` **hoàn toàn KHÔNG tự phát ra điện 5V**.
  * Nếu cắm 2 dây của bơm trực tiếp vào `COM` và `NO` thì bơm sẽ không có nguồn điện (mạch hở).
  * **Cách đấu chuẩn:** Phải mắc **nối tiếp** nguồn $5\,\text{V}$ qua tiếp điểm Relay:
    1. Cực dương nguồn $5\,\text{V}$ (Dây đỏ) $\rightarrow$ Chân **`COM`** của Relay.
    2. Chân **`NO`** của Relay $\rightarrow$ Dây đỏ ($+$) của Máy bơm mini.
    3. Dây đen ($-$) của Máy bơm mini $\rightarrow$ Nối thẳng vào **GND** của nguồn $5\,\text{V}$ (và nối chung GND ESP32).
* **Nguyên nhân Servo Van không quay:**
  1. **Nút bấm trên Web phân tách độc lập:** Nút `Bật/Tắt Bơm (Manual)` **chỉ** điều khiển máy bơm. Để xoay van, bạn phải bấm vào các nút riêng biệt: **`Van 0% (Đóng)`**, **`Van 50% (Mở Nửa)`**, hoặc **`Van 100% (Mở Hết)`**.
  2. **Nguồn cấp Servo SG90:** Dây đỏ của Servo phải cắm vào chân **`5V / VIN`** của ESP32 (hoặc nguồn $5\,\text{V}$ ngoài). Cắm vào chân $3.3\,\text{V}$ sẽ không đủ điện áp và dòng làm mô tơ rung giật hoặc đứng im.
  3. **Khởi tạo Timer xung PWM:** Firmware đã được bổ sung cấu hình `ESP32PWM::allocateTimer(0..3)` và `setPeriodHertz(50)` để chống xung đột Timer giữa Servo và còi Buzzer. Nạp lại firmware mới nhất để đồng bộ.
