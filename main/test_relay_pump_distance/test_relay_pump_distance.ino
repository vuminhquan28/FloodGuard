/**
 * ============================================================================
 * CHƯƠNG TRÌNH KIỂM THỬ: RELAY & MÁY BƠM DỰA TRÊN KHOẢNG CÁCH (HC-SR04)
 * Dự án: FloodGuard - Trạm Cảnh Báo & Thoát Lũ Tự Động
 * ============================================================================
 * 
 * SƠ ĐỒ CHÂN KẾT NỐI (PINOUT):
 * 1. Cảm biến siêu âm HC-SR04:
 *    - VCC  ──► 5V (hoặc VIN)
 *    - GND  ──► GND
 *    - Trig ──► GPIO 13
 *    - Echo ──► GPIO 12 (khuyên dùng qua trở bảo vệ hoặc nối trực tiếp)
 * 
 * 2. Module Relay 5V (Điều khiển Máy Bơm):
 *    - VCC  ──► 5V (VIN ESP32 hoặc nguồn 5V ngoài)
 *    - GND  ──► GND (nối chung GND ESP32)
 *    - IN   ──► GPIO 23 (Active LOW)
 * 
 * 3. Đấu nối Máy Bơm Mini qua Relay (MẮC NỐI TIẾP TIẾP ĐIỂM KHÔ):
 *    - Nguồn (+) 5V ngoài  ──► Chân COM của Relay
 *    - Chân NO của Relay   ──► Dây ĐỎ (+) của Máy Bơm
 *    - Dây ĐEN (-) của Bơm ──► Nối chung vào GND nguồn 5V ngoài & GND ESP32
 * 
 * NGUYÊN LÝ HOẠT ĐỘNG KIỂM THỬ:
 * - Khi khởi động (setup): Bật Relay trong 2 giây (tự kiểm tra bơm), sau đó tắt.
 * - Trong vòng lặp (loop):
 *   + Đưa tay lại gần HC-SR04 (< 15 cm, mô phỏng nước ngập dâng cao):
 *     --> RELAY ĐÓNG (Đèn xanh relay SÁNG) --> MÁY BƠM CHẠY
 *   + Rút tay ra xa HC-SR04 (> 20 cm, mô phỏng nước đã rút an toàn):
 *     --> RELAY NHẢ (Đèn xanh relay TẮT)  --> MÁY BƠM DỪNG
 *   + Dải trễ 5 cm (15 - 20 cm) giúp chống rung giật relay.
 * ============================================================================
 */

#include <Arduino.h>

// Định nghĩa chân phần cứng
#define PIN_TRIG        13   // Chân phát xung cảm biến siêu âm
#define PIN_ECHO        12   // Chân thu xung phản xạ
#define PIN_RELAY       23   // Kích relay máy bơm 5V (Active LOW)

// Tùy chọn LED hiển thị bổ trợ (nếu có cắm trên mạch)
#define PIN_LED_GREEN   21   // LED Xanh: An toàn / Bơm Tắt
#define PIN_LED_RED     18   // LED Đỏ: Báo động / Bơm Bật

// Ngưỡng khoảng cách điều khiển bơm (đơn vị: cm)
const float DISTANCE_PUMP_ON  = 15.0; // Khoảng cách < 15cm: Nước dâng / tay gần -> BẬT BƠM
const float DISTANCE_PUMP_OFF = 20.0; // Khoảng cách > 20cm: Nước rút / tay xa  -> TẮT BƠM

bool isPumpActive = false;
unsigned long lastLogTime = 0;

// ==========================================
// HÀM ĐIỀU KHIỂN RELAY MÁY BƠM (KỸ THUẬT HIGH-Z)
// ==========================================
void setPump(bool enable) {
  isPumpActive = enable;
  if (enable) {
    // Kéo LOW kích optocoupler đóng tiếp điểm COM - NO
    pinMode(PIN_RELAY, OUTPUT);
    digitalWrite(PIN_RELAY, LOW);

    // Cập nhật LED bổ trợ
    digitalWrite(PIN_LED_RED, HIGH);
    digitalWrite(PIN_LED_GREEN, LOW);
  } else {
    // Thả nổi High-Z (INPUT) để triệt tiêu hoàn toàn dòng rò 1.7mA qua optocoupler 5V
    pinMode(PIN_RELAY, INPUT);

    // Cập nhật LED bổ trợ
    digitalWrite(PIN_LED_RED, LOW);
    digitalWrite(PIN_LED_GREEN, HIGH);
  }
}

// ==========================================
// ĐỌC KHOẢNG CÁCH SIÊU ÂM (BỘ LỌC TRUNG VỊ 3 MẪU)
// ==========================================
float readDistanceCM() {
  float samples[3];
  for (int i = 0; i < 3; i++) {
    digitalWrite(PIN_TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(PIN_TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(PIN_TRIG, LOW);

    // Timeout 25000us ~ tối đa 4.2m
    long duration = pulseIn(PIN_ECHO, HIGH, 25000);
    if (duration == 0) {
      samples[i] = 999.0; // Không nhận được echo
    } else {
      samples[i] = (duration * 0.0343) / 2.0;
    }
    delay(10); // Khoảng cách giãn giữa các lần bắn sóng
  }

  // Sắp xếp tìm giá trị trung vị (Median filter)
  if (samples[0] > samples[1]) { float t = samples[0]; samples[0] = samples[1]; samples[1] = t; }
  if (samples[1] > samples[2]) { float t = samples[1]; samples[1] = samples[2]; samples[2] = t; }
  if (samples[0] > samples[1]) { float t = samples[0]; samples[0] = samples[1]; samples[1] = t; }

  return samples[1]; // Trả về mẫu ở giữa
}

// ==========================================
// KHỞI TẠO (SETUP)
// ==========================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n========================================================");
  Serial.println("   FLOODGUARD - TEST RELAY VA MAY BOM THEO KHOANG CACH   ");
  Serial.println("========================================================");

  // Cấu hình chân cảm biến siêu âm
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);

  // Cấu hình chân LED bổ trợ
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_RED, OUTPUT);

  // 1. Tự kiểm tra Relay khi khởi động (Self-test)
  Serial.println("[TEST BƯỚC 1] Khoi dong kiem tra Relay & May Bom trong 2 giay...");
  Serial.println(">> RELAY: DONG (Nghe tach, den xanh Relay SANG)");
  setPump(true);
  delay(2000);

  Serial.println(">> RELAY: NHA (Den xanh Relay TAT)");
  setPump(false);
  delay(1000);

  Serial.println("\n[TEST BƯỚC 2] Bat dau do khoang cach HC-SR04 thoi gian thuc:");
  Serial.printf(" - Dua tay/vat the lai gan (< %.1f cm) -> BOM SE BAT\n", DISTANCE_PUMP_ON);
  Serial.printf(" - Rut tay/vat the ra xa   (> %.1f cm) -> BOM SE TAT\n", DISTANCE_PUMP_OFF);
  Serial.println("--------------------------------------------------------\n");
}

// ==========================================
// VÒNG LẶP CHÍNH (LOOP)
// ==========================================
void loop() {
  // 1. Đọc khoảng cách từ HC-SR04
  float dist = readDistanceCM();

  // 2. Logic điều khiển Relay có Hysteresis
  if (dist < DISTANCE_PUMP_ON && dist > 1.0) {
    if (!isPumpActive) {
      Serial.println("\n [CANH BAO] Vat the lai gan -> DONG RELAY -> BAT BOM!");
      setPump(true);
    }
  } else if (dist > DISTANCE_PUMP_OFF) {
    if (isPumpActive) {
      Serial.println("\n [AN TOAN] Vat the ra xa -> NHA RELAY -> TAT BOM!");
      setPump(false);
    }
  }

  // 3. In dữ liệu ra Serial Monitor mỗi 300ms
  if (millis() - lastLogTime >= 300) {
    lastLogTime = millis();

    Serial.printf("Khoang cach: %5.1f cm | Trạng thái Bơm: [%s] | Relay Pin: %s\n",
      (dist > 500.0) ? -1.0 : dist,
      isPumpActive ? ">> DANG BAT (ON) <<" : "   DA TAT (OFF)   ",
      isPumpActive ? "LOW (Active)" : "High-Z (Floating)"
    );

    // Lời nhắc kiểm tra điện áp nếu đèn xanh sáng mà bơm không quay
    static int reminderCounter = 0;
    if (isPumpActive && ++reminderCounter % 15 == 0) {
      Serial.println("\n*** LUU Y KIEM TRA PHAN CUNG:");
      Serial.println("Neu den xanh Relay SANG ma May Bom KHONG CHAY:");
      Serial.println("1. Chan COM Relay da noi vao Nguon (+) 5V chua?");
      Serial.println("2. Chan NO Relay da noi vao Day Do (+) cua Bom chua?");
      Serial.println("3. Day Den (-) cua Bom da noi vao GND chung chua?\n");
    }
  }

  delay(100);
}

