/**
 * ============================================================================
 * CHƯƠNG TRÌNH KIỂM THỬ & CÂN CHỈNH GÓC QUAY SERVO SG90 (VAN XẢ NƯỚC)
 * Dự án: FloodGuard - Trạm Cảnh Báo & Thoát Lũ Tự Động
 * Tệp: test_servo_sg90.ino (Nằm trong thư mục main)
 * ============================================================================
 * 
 * 1. SƠ ĐỒ ĐẤU DÂY SERVO SG90 VỚI ESP32:
 *    - Dây NÂU (hoặc ĐEN)  ──► Chân GND của ESP32 (hoặc GND nguồn ngoài)
 *    - Dây ĐỎ              ──► Chân 5V / VIN của ESP32 (LƯU Ý: KHÔNG cắm vào 3.3V)
 *    - Dây CAM (hoặc VÀNG) ──► Chân GPIO 27 (Chân PWM điều khiển van)
 * 
 * 2. VÌ SAO SERVO QUAY KHÔNG ĐÚNG HƯỚNG?
 *    Hiện tượng servo không quay đúng hướng khi gắn vào mô hình thường do 2 nguyên nhân:
 *    - Nguyên nhân A (Lắp cánh tay sai mốc 0° - Phổ biến nhất 90%):
 *      Khi mua về hoặc khi chưa cấp điện, cốt răng servo đang nằm ở góc ngẫu nhiên.
 *      Nếu bạn lắp cánh tay nhựa vào trước rồi mới cấp điện, servo sẽ bị giật và quay
 *      sai hoàn toàn cung chuyển động cơ học (có thể đập vào thành bể hoặc không đóng kín).
 *    - Nguyên nhân B (Chiều cơ học bị nghịch do vị trí đặt servo):
 *      Tùy theo việc bạn đặt servo bên trái hay bên phải máng xả lũ, van nâng lên hay kéo xuống:
 *      + Chiều Thuận (Mặc định):  0° = Đóng kín (0%),  90° = Nửa (50%), 180° = Mở toang (100%)
 *      + Chiều Nghịch (Đảo chiều): 180° = Đóng kín (0%), 90° = Nửa (50%), 0° = Mở toang (100%)
 * 
 * 3. HƯỚNG DẪN 4 BƯỚC CÂN CHỈNH & LẮP RÁP CÁNH TAY SERVO CHUẨN:
 *    - Bước 1: Nạp code này vào ESP32 và mở Serial Monitor (tốc độ 115200).
 *    - Bước 2: THÁO CÁNH TAY NHỰA RA KHỎI TRỤC SERVO (để trục quay tự do).
 *    - Bước 3: Gõ lệnh "0" trên Serial Monitor (hoặc chọn phím 1).
 *              Servo sẽ quay cốt răng về đúng vị trí mốc 0° điện tử cố định.
 *    - Bước 4: Giữ nguyên nguồn điện, lúc này cầm cánh tay nhựa ướm vào trục sao cho
 *              cánh van NẰM Ở TRẠNG THÁI ĐÓNG KÍN CỬA XẢ, rồi ấn chặt và vặn ốc định vị!
 *              (Nếu mô hình của bạn cần góc 180° là đóng, xem mục đảo chiều bên dưới).
 * ============================================================================
 */

#include <Arduino.h>
#include <ESP32Servo.h>

#define PIN_SERVO 27 // Chân PWM điều khiển van xả nước

Servo valveServo;

// ==========================================
// CẤU HÌNH CHIỀU QUAY CƠ HỌC (THUẬN HOẶC NGHỊCH)
// ==========================================
// Nếu lắp thực tế thấy góc mở bị ngược (báo mở 100% mà cửa lại đóng kín):
// Hãy đổi giá trị này thành true:
bool REVERSE_DIRECTION = false;

// Trạng thái vận hành
int currentAngle = 0;
bool isManualMode = false; // Mặc định chạy demo tự động; gõ Serial để can thiệp thủ công

// ==========================================
// HÀM CHUYỂN ĐỔI GÓC THEO CHIỀU CƠ HỌC
// ==========================================
int mapMechanicalAngle(int logicalAngle) {
  // Ràng buộc góc trong phạm vi 0 - 180
  logicalAngle = constrain(logicalAngle, 0, 180);
  
  if (REVERSE_DIRECTION) {
    return 180 - logicalAngle; // Đảo chiều quay: 0° thành 180°, 180° thành 0°
  } else {
    return logicalAngle;       // Chiều thuận chuẩn
  }
}

// ==========================================
// HÀM QUAY SERVO MƯỢT MÀ (TRÁNH GIẬT HỎNG NHÔNG)
// ==========================================
void moveServoSmooth(int targetLogicalAngle, int stepDelayMs = 12) {
  int targetPhys = mapMechanicalAngle(targetLogicalAngle);
  int startPhys  = mapMechanicalAngle(currentAngle);

  Serial.printf(">> Chuyen van tu %d do sang %d do (Vat ly: %d -> %d)... ",
                currentAngle, targetLogicalAngle, startPhys, targetPhys);

  if (startPhys < targetPhys) {
    for (int pos = startPhys; pos <= targetPhys; pos++) {
      valveServo.write(pos);
      delay(stepDelayMs);
    }
  } else {
    for (int pos = startPhys; pos >= targetPhys; pos--) {
      valveServo.write(pos);
      delay(stepDelayMs);
    }
  }
  currentAngle = targetLogicalAngle;
  Serial.println("XONG!");
}

// In menu điều khiển ra Serial Monitor
void printMenu() {
  Serial.println("\n========================================================");
  Serial.println("  FLOODGUARD - TOOL CÂN CHỈNH & TEST SERVO SG90 (GPIO 27) ");
  Serial.println("========================================================");
  Serial.printf(" Chieu quay hien tai: [%s]\n", REVERSE_DIRECTION ? "NGHICH (REVERSED)" : "THUAN (NORMAL)");
  Serial.printf(" Goc van hien tai   : [%d do] (Vat ly: %d do)\n", currentAngle, mapMechanicalAngle(currentAngle));
  Serial.println("--------------------------------------------------------");
  Serial.println(" [1] Van DONG HOAN TOAN  ( 0 do)  - Muc NORMAL / WARNING");
  Serial.println(" [2] Van MO MOT NUA      (90 do)  - Muc DANGER (50%)");
  Serial.println(" [3] Van MO TOANG TOI DA (180 do) - Muc CRITICAL (100%)");
  Serial.println(" [S] Chay quet kiem tra (Sweep 0 -> 180 -> 0 do)");
  Serial.println(" [R] Dao chieu quay Thuan <-> Nghich");
  Serial.println(" [Nhap so 0-180] vi du: 45, 120 de quay goc tuy chon");
  Serial.println("========================================================\n");
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  // 1. Cấu hình cấp phát Timer phần cứng chuẩn cho ESP32
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  // 2. Khởi tạo tần số 50Hz chuẩn của SG90 (chu kỳ 20ms)
  valveServo.setPeriodHertz(50);

  // 3. Gắn servo vào GPIO 27 với dải xung chuẩn 500us - 2400us
  valveServo.attach(PIN_SERVO, 500, 2400);

  // 4. Đưa servo về vị trí 0 độ ban đầu
  int initialPhys = mapMechanicalAngle(0);
  valveServo.write(initialPhys);
  currentAngle = 0;

  printMenu();
  Serial.println(">>> DANG CHAY CHẾ ĐỘ DEMO TU DONG (Moi nac giu 3 giay).");
  Serial.println(">>> Go phim 1, 2, 3 hoac goc bat ky vao Serial de chuyen sang che do can chinh thu cong!\n");
}

void handleSerialCommand() {
  if (!Serial.available()) return;

  String input = Serial.readStringUntil('\n');
  input.trim();
  if (input.length() == 0) return;

  isManualMode = true; // Chuyển sang can thiệp thủ công

  if (input.equalsIgnoreCase("1")) {
    Serial.println("\n[LENH 1] Dua van ve DONG KIN (0 do)");
    moveServoSmooth(0);
  } else if (input.equalsIgnoreCase("2")) {
    Serial.println("\n[LENH 2] Dua van MO 50% (90 do)");
    moveServoSmooth(90);
  } else if (input.equalsIgnoreCase("3")) {
    Serial.println("\n[LENH 3] Dua van MO TOANG 100% (180 do)");
    moveServoSmooth(180);
  } else if (input.equalsIgnoreCase("R")) {
    REVERSE_DIRECTION = !REVERSE_DIRECTION;
    Serial.printf("\n[LENH R] Da dao chieu quay thanh: [%s]\n",
                  REVERSE_DIRECTION ? "NGHICH (REVERSED)" : "THUAN (NORMAL)");
    // Cập nhật lại vị trí vật lý ngay lập tức
    int newPhys = mapMechanicalAngle(currentAngle);
    valveServo.write(newPhys);
    Serial.printf(">> Goc vat ly moi xuat ra servo: %d do\n", newPhys);
  } else if (input.equalsIgnoreCase("S")) {
    Serial.println("\n[LENH S] Bat dau kiem tra quet toan dai (Sweep)...");
    moveServoSmooth(0, 8);
    delay(500);
    moveServoSmooth(180, 8);
    delay(500);
    moveServoSmooth(0, 8);
    Serial.println(">> Hoan thanh quet toan dai!");
  } else {
    // Kiểm tra xem người dùng có nhập góc số cụ thể không
    int customAngle = input.toInt();
    if (customAngle >= 0 && customAngle <= 180) {
      Serial.printf("\n[LENH TUY CHINH] Quay van den goc %d do\n", customAngle);
      moveServoSmooth(customAngle);
    } else {
      Serial.println("[LOI] Lenh khong hop le! Vui long nhap 1, 2, 3, S, R hoac so tu 0 den 180.");
      printMenu();
    }
  }
}

void loop() {
  // Tiếp nhận và xử lý lệnh từ người dùng qua Serial Monitor
  handleSerialCommand();

  // Nếu người dùng chưa gõ gì thì chạy chu trình tự động minh họa 3 trạng thái
  if (!isManualMode) {
    static unsigned long lastAutoStep = 0;
    static int autoPhase = 0;

    if (millis() - lastAutoStep >= 3500) {
      lastAutoStep = millis();
      if (autoPhase == 0) {
        Serial.println("[AUTO DEMO] -> Mo phong NORMAL / WARNING: Van DONG (0 do)");
        moveServoSmooth(0);
        autoPhase = 1;
      } else if (autoPhase == 1) {
        Serial.println("[AUTO DEMO] -> Mo phong DANGER: Van MO 50% (90 do)");
        moveServoSmooth(90);
        autoPhase = 2;
      } else if (autoPhase == 2) {
        Serial.println("[AUTO DEMO] -> Mo phong CRITICAL: Van MO TOANG (180 do)");
        moveServoSmooth(180);
        autoPhase = 0;
      }
    }
  }

  delay(20);
}

