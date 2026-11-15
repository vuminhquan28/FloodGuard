#include <Arduino.h>
#include <ESP32Servo.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>

// ==========================================
// CẤU HÌNH PHẦN CỨNG THẬT (ESP32 HARDWARE)
// Chế độ: SoftAP (ESP32 tự phát Wi-Fi)
// ==========================================
#define PIN_TRIG        13   // Cảm biến siêu âm Trig (D13 - Lỗ g38 bo trái)
#define PIN_ECHO        12   // Cảm biến siêu âm Echo (D12 - Lỗ g37 bo trái - qua trở hạn dòng)
#define PIN_RAIN_DO     34   // Cảm biến mưa Digital Out (D34 - Lỗ b31 bo phải - Input-only)
#define PIN_RAIN_ADC    35   // Cảm biến mưa Analog Out (D35 - Lỗ b32 bo phải - Input-only)
#define PIN_SERVO       27   // Điều khiển van xả nước SG90 PWM (D27 - Lỗ g35 bo trái)
#define PIN_RELAY       23   // Điều khiển Relay máy bơm 5V (D23 - Lỗ b37 bo phải - Active LOW)
#define PIN_BUZZER      4    // Còi báo động Active Buzzer 5V (D4 - Lỗ b34 bo phải)
#define PIN_LED_GREEN   21   // LED trạng thái NORMAL (D21 - Lỗ b36 bo phải)
#define PIN_LED_YELLOW  19   // LED trạng thái WARNING (D19 - Lỗ b38 bo phải)
#define PIN_LED_RED     18   // LED trạng thái DANGER / CRITICAL (D18 - Lỗ b39 bo phải)

// Thông tin mạng Wi-Fi do ESP32 tự phát (SoftAP)
const char* AP_SSID = "FloodGuard_AP";
const char* AP_PASS = "12345678"; // Tối thiểu 8 ký tự

// ==========================================
// THÔNG SỐ ĐO VÀ NGƯỠNG MỰC NƯỚC (DEMO TÍNH TỪ ĐÁY BỂ LÊN)
// Khoảng cách đáy hồ khi cạn: DISTANCE_EMPTY = 10.0cm
// Cột nước từ đáy bể lên: h = DISTANCE_EMPTY - d = 10.0cm - d
// - An toàn (NORMAL)   : 0.0cm - 1.5cm  -> P < 19%   (d > 8.5cm)
// - Cảnh báo (WARNING) : 1.5cm - 3.0cm  -> 19% - 37%  (7.0cm <= d <= 8.5cm)
// - Nguy hiểm (DANGER) : 3.0cm - 4.5cm  -> 38% - 55%  (5.5cm <= d < 7.0cm)
// - Báo động (CRITICAL): > 4.5cm        -> P >= 56%   (d < 5.5cm)
// ==========================================
const float DISTANCE_EMPTY = 10.0;  // Khoảng cách đáy hồ khi cạn (cm) - 0%
const float DISTANCE_FULL  = 2.0;   // Khoảng cách mép đầy tràn (cm) - 100% (vùng mù cảm biến >= 2cm)

// Dải trễ (Hysteresis) FSM - Vào trạng thái mực nước
const int THRESHOLD_WARN_ENTER   = 19; // h >= 1.5cm (d <= 8.5cm)
const int THRESHOLD_DANGER_ENTER = 38; // h >= 3.0cm (d <= 7.0cm)
const int THRESHOLD_CRIT_ENTER   = 56; // h >= 4.5cm (d <= 5.5cm)

// Dải trễ (Hysteresis) FSM - Thoát trạng thái (khi nước rút, Delta = 3% ~ 2.4mm)
const int THRESHOLD_CRIT_EXIT    = 53; // h < 4.24cm (d > 5.76cm)
const int THRESHOLD_DANGER_EXIT  = 35; // h < 2.80cm (d > 7.20cm)
const int THRESHOLD_WARN_EXIT    = 16; // h < 1.28cm (d > 8.72cm)

// ==========================================
// CẤP ĐỘ CẢM BIẾN MƯA (ESP32 ADC 12-bit: 0 - 4095)
// ==========================================
// - Khô ráo (Không mưa): ADC ~ 3200 - 4095
// - Mưa nhỏ / Vài giọt (Light Rain): ADC < 2800 hoặc DO == LOW -> Mức WARNING
// - Mưa to / Nhúng 1 phần (Heavy Rain): ADC < 1800 -> Mức DANGER (Bơm BẬT, Van 50%)
// - Nhúng hết vào nước / Mưa bão cực to (Submerged): ADC < 1100 -> Mức CRITICAL (Bơm BẬT, Van 100%)
const int RAIN_ADC_LIGHT       = 2800;
const int RAIN_ADC_HEAVY       = 1800;
const int RAIN_ADC_SUBMERGED   = 1100;

// Các trạng thái của hệ thống (FSM)
enum SystemState {
  STATE_NORMAL,
  STATE_WARNING,
  STATE_DANGER,
  STATE_CRITICAL
};

// ==========================================
// BIẾN TOÀN CỤC & THIẾT BỊ NGOẠI VI
// ==========================================
Servo valveServo;
WebServer server(80);

SystemState sysState  = STATE_NORMAL;
int waterPercent      = 0;
float currentDistance = 10.0;
float lastValidDistance = 10.0; // Giá trị hợp lệ gần nhất (Median Filter fallback)
bool isRaining        = false;
int rainRawADC        = 0;

bool pumpState        = false;
int valvePercent      = 0; // 0%, 50%, 100%
bool isAutoMode       = true;

// Biến điều khiển thời gian non-blocking
unsigned long lastSensorRead   = 0;
unsigned long lastDebugPrint   = 0;  // Debug Serial mỗi 2 giây
bool buzzerToggle              = false;

// ==========================================
// [KỸ THUẬT 2] ĐỌC CẢM BIẾN - MEDIAN FILTER 3 MẪU
// Chống nhiễu EMI từ Relay/Motor bơm (xung gai điện từ làm pulseIn() timeout)
// ==========================================

// Đọc 1 mẫu khoảng cách từ HC-SR04 (trả về -1.0 nếu timeout hoặc ngoài dải)
float readUltrasonicSingleCM() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  long duration = pulseIn(PIN_ECHO, HIGH, 30000); // Timeout 30ms (~5m)
  if (duration <= 0) return -1.0f;

  float dist = (duration * 0.0343f) / 2.0f;
  // Loại bỏ mẫu ngoài dải vật lý hợp lệ (2cm - 300cm)
  if (dist < 2.0f || dist > 300.0f) return -1.0f;
  return dist;
}

// Lấy trung vị (Median) của 3 mẫu cách nhau 12ms
// - Loại bỏ mẫu đột biến do EMI (nhiễu đỉnh)
// - Nếu cả 3 đều lỗi: giữ nguyên lastValidDistance
float readUltrasonicCM() {
  float samples[3];
  int validCount = 0;

  for (int i = 0; i < 3; i++) {
    samples[i] = readUltrasonicSingleCM();
    if (samples[i] > 0) validCount++;
    if (i < 2) delay(12); // Khoảng cách giữa các lần phát xung (10-15ms)
  }

  // Nếu cả 3 mẫu đều lỗi (sụt áp thoáng qua khi relay đóng ngắt)
  // -> giữ giá trị hợp lệ gần nhất tránh FSM nhảy lung tung
  if (validCount == 0) return lastValidDistance;

  // Bubble sort 3 phần tử: đẩy các mẫu -1 (lỗi) lên đầu mảng
  for (int i = 0; i < 2; i++) {
    for (int j = 0; j < 2 - i; j++) {
      if (samples[j] < 0 || (samples[j+1] > 0 && samples[j] > samples[j+1])) {
        float tmp    = samples[j];
        samples[j]   = samples[j+1];
        samples[j+1] = tmp;
      }
    }
  }

  float result = lastValidDistance;
  if (validCount == 1) {
    // Chỉ có 1 mẫu hợp lệ - dùng luôn
    for (int i = 0; i < 3; i++) { if (samples[i] > 0) { result = samples[i]; break; } }
  } else if (validCount == 2) {
    // 2 mẫu hợp lệ - lấy trung bình
    float sum = 0; int cnt = 0;
    for (int i = 0; i < 3; i++) { if (samples[i] > 0) { sum += samples[i]; cnt++; } }
    result = sum / cnt;
  } else {
    // 3 mẫu đều hợp lệ - lấy phần tử giữa (Median)
    result = samples[1];
  }

  lastValidDistance = result; // Cập nhật fallback
  return result;
}

void updateSensors() {
  float d = readUltrasonicCM();
  if (d < DISTANCE_FULL)  d = DISTANCE_FULL;
  if (d > DISTANCE_EMPTY) d = DISTANCE_EMPTY;
  currentDistance = d;

  // Tính phần trăm mực nước (10.0cm = 0%, 2.0cm = 100%)
  float pct = ((DISTANCE_EMPTY - currentDistance) / (DISTANCE_EMPTY - DISTANCE_FULL)) * 100.0f;
  waterPercent = (int)constrain(pct, 0.0f, 100.0f);

  // Đọc cảm biến mưa (Chân DO GPIO 34 và AO GPIO 35)
  // - DO: LOW khi phát hiện đọng nước mưa (qua bộ so sánh LM393)
  // - AO: ADC 12-bit (0 - 4095), điện trở giảm khi có nước tiếp xúc
  rainRawADC = analogRead(PIN_RAIN_ADC);
  bool rainDO = (digitalRead(PIN_RAIN_DO) == LOW);
  isRaining = rainDO || (rainRawADC < RAIN_ADC_LIGHT);

  // [DEBUG] In ra Serial Monitor mỗi 1 giây để theo dõi rõ các giá trị
  static unsigned long lastSensorLog = 0;
  if (millis() - lastSensorLog >= 1000) {
    lastSensorLog = millis();
    const char* rainLevelStr = (rainRawADC < RAIN_ADC_SUBMERGED) ? "NGAP_NUOC (CRITICAL)" :
                               (rainRawADC < RAIN_ADC_HEAVY)     ? "MUA_TO (DANGER)" :
                               (isRaining)                       ? "MUA_NHO (WARNING)" : "KHO_RAO (NORMAL)";
    float waterHeight = DISTANCE_EMPTY - currentDistance;
    if (waterHeight < 0.0f) waterHeight = 0.0f;
    Serial.printf("[SENSOR] Dist=%.1fcm | NuocDay=%.1fcm (%d%%) | RainDO=%d | RainADC=%d | Muc: %s\n",
      currentDistance, waterHeight, waterPercent, rainDO ? 1 : 0, rainRawADC, rainLevelStr);
  }
}

// ==========================================
// THUẬT TOÁN FSM VÀ HYSTERESIS
// ==========================================
void evaluateSystemStateAuto() {
  // Xác định các cấp độ mưa
  bool isLightRain = isRaining;                         // ADC < 2800 hoặc DO == LOW (Mưa nhỏ)
  bool isHeavyRain = (rainRawADC < RAIN_ADC_HEAVY);     // ADC < 1800 (Mưa to / nhúng 1 phần)
  bool isSubmerged = (rainRawADC < RAIN_ADC_SUBMERGED); // ADC < 1100 (Nhúng ngập hết vào nước / mưa xối xả)

  // --- Chuyển trạng thái FSM (kết hợp cả Mực nước và Cảm biến mưa) ---
  // Luôn đánh giá để cập nhật hiển thị LED, Còi và giám sát an toàn Failsafe
  switch (sysState) {

    case STATE_NORMAL:
      if (waterPercent >= THRESHOLD_CRIT_ENTER || isSubmerged) {
        sysState = STATE_CRITICAL; // Mực nước ngập sâu hoặc nhúng chìm cảm biến mưa
      } else if (waterPercent >= THRESHOLD_DANGER_ENTER || isHeavyRain || (isLightRain && waterPercent >= THRESHOLD_WARN_ENTER)) {
        sysState = STATE_DANGER;   // Mực nước nguy hiểm hoặc mưa to
      } else if (waterPercent >= THRESHOLD_WARN_ENTER || isLightRain) {
        sysState = STATE_WARNING;  // Mực nước dâng hoặc có mưa nhỏ
      }
      break;

    case STATE_WARNING:
      if (waterPercent >= THRESHOLD_CRIT_ENTER || isSubmerged) {
        sysState = STATE_CRITICAL;
      } else if (waterPercent >= THRESHOLD_DANGER_ENTER || isHeavyRain || (isLightRain && waterPercent >= THRESHOLD_DANGER_ENTER)) {
        sysState = STATE_DANGER;
      } else if (waterPercent < THRESHOLD_WARN_EXIT && !isLightRain) {
        sysState = STATE_NORMAL;   // Nước cạn và tạnh mưa hoàn toàn
      }
      break;

    case STATE_DANGER:
      if (waterPercent >= THRESHOLD_CRIT_ENTER || isSubmerged || (isHeavyRain && waterPercent >= THRESHOLD_DANGER_ENTER)) {
        sysState = STATE_CRITICAL;
      } else if (waterPercent < THRESHOLD_DANGER_EXIT && !isHeavyRain) {
        sysState = STATE_WARNING;  // Nước rút và lượng mưa giảm
      }
      break;

    case STATE_CRITICAL:
      if (waterPercent < THRESHOLD_CRIT_EXIT && !isSubmerged) {
        sysState = STATE_DANGER;   // Rút khỏi mức ngập nghiêm trọng (dưới 53%)
      }
      break;
  }

  // --- Điều khiển Bơm và Van theo trạng thái FSM (CHỈ KHI Ở CHẾ ĐỘ AUTO) ---
  if (isAutoMode) {
    switch (sysState) {
      case STATE_NORMAL:
      case STATE_WARNING:
        pumpState    = false;
        valvePercent = 0;    // Van đóng hoàn toàn 0°
        break;

      case STATE_DANGER:
        pumpState    = true; // BẬT máy bơm 5V
        valvePercent = 50;   // Mở van thoát lũ 50% (90°)
        break;

      case STATE_CRITICAL:
        pumpState    = true; // BẬT máy bơm 5V
        valvePercent = 100;  // Mở van thoát lũ tối đa 100% (180°)
        break;
    }
  }
  // KHI Ở MANUAL MODE:
  // pumpState và valvePercent do người quản lý hoàn toàn kiểm soát qua Web,
  // FSM tuyệt đối không ghi đè giá trị Bơm và Van.
  // Đèn LED và Còi vẫn chạy tự động 100% theo sysState.

  // [DEBUG] In trạng thái FSM ra Serial khi có thay đổi
  static SystemState lastDebugState = (SystemState)99;
  if (sysState != lastDebugState) {
    const char* stNames[] = {"NORMAL", "WARNING", "DANGER", "CRITICAL"};
    Serial.printf("\n>>> [FSM CHUYEN TRANG THAI] %s (%s) | Nuoc: %d%% | RainADC: %d | Bom: %s | Van: %d%%\n\n",
      stNames[sysState], isAutoMode ? "AUTO" : "MANUAL", waterPercent, rainRawADC, pumpState ? "BAT" : "TAT", valvePercent);
    lastDebugState = sysState;
  }
}

// ==========================================
// ÁP ĐẶT ĐẦU RA (ACTUATORS & LEDS)
// ==========================================
void applyOutputs() {
  // [KỸ THUẬT 1] Điều khiển Relay bằng High-Z (INPUT) khi tắt bơm
  if (pumpState) {
    pinMode(PIN_RELAY, OUTPUT);
    digitalWrite(PIN_RELAY, LOW);   // LOW -> opto kích -> Relay đóng -> Bơm BẬT
  } else {
    pinMode(PIN_RELAY, INPUT);      // High-Z -> triệt tiêu hoàn toàn dòng rò -> Bơm TẮT hoàn toàn
  }

  // 2. Góc mở Servo (0% = 0°, 50% = 90°, 100% = 180°)
  // CHỈ GHI XUNG (write) KHI GÓC THAY ĐỔI
  // Khi vẫn đang ở cùng mức cảnh báo, tay quay giữ nguyên vị trí ổn định tuyệt đối
  static int currentServoAngle = -1;
  int targetAngle = map(valvePercent, 0, 100, 0, 180);
  targetAngle = constrain(targetAngle, 0, 180);
  if (targetAngle != currentServoAngle) {
    valveServo.write(targetAngle);
    currentServoAngle = targetAngle;
    Serial.printf("[SERVO] Xoay goc: %d do (Van %d%%)\n", targetAngle, valvePercent);
  }

  // [KỸ THUẬT 3] Đèn LED & Còi Buzzer đa cấp độ - TỰ ĐỘNG THEO SYSSTATE Ở CẢ AUTO VÀ MANUAL
  // Còi Active Buzzer 5V: Dùng digitalWrite HIGH/LOW, KHÔNG dùng tone()/noTone()
  // để tránh xung đột kênh Timer LEDC với Servo PWM làm servo nhảy loạn xạ.
  unsigned long now = millis();
  switch (sysState) {
    case STATE_NORMAL:
      digitalWrite(PIN_LED_GREEN, HIGH);
      digitalWrite(PIN_LED_YELLOW, LOW);
      digitalWrite(PIN_LED_RED, LOW);
      digitalWrite(PIN_BUZZER, LOW);
      break;

    case STATE_WARNING:
      // LED vàng sáng, còi bíp nhẹ ngắt quãng thưa (chu kỳ 1500ms: kêu 120ms, tắt 1380ms)
      digitalWrite(PIN_LED_GREEN, LOW);
      digitalWrite(PIN_LED_YELLOW, HIGH);
      digitalWrite(PIN_LED_RED, LOW);
      digitalWrite(PIN_BUZZER, (now % 1500 < 120) ? HIGH : LOW);
      break;

    case STATE_DANGER:
      // LED đỏ sáng, còi bíp dồn dập (chu kỳ 300ms: kêu 150ms, tắt 150ms)
      digitalWrite(PIN_LED_GREEN, LOW);
      digitalWrite(PIN_LED_YELLOW, LOW);
      digitalWrite(PIN_LED_RED, HIGH);
      digitalWrite(PIN_BUZZER, (now % 300 < 150) ? HIGH : LOW);
      break;

    case STATE_CRITICAL:
      // LED đỏ chớp nháy nhanh (chu kỳ 100ms), còi kêu liên tục
      digitalWrite(PIN_LED_GREEN, LOW);
      digitalWrite(PIN_LED_YELLOW, LOW);
      digitalWrite(PIN_LED_RED, (now % 100 < 50) ? HIGH : LOW);
      digitalWrite(PIN_BUZZER, HIGH);
      break;
  }
}

// ==========================================
// WEB SERVER DASHBOARD (HTML / CSS / JS)
// ==========================================
const char HTML_DASHBOARD[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FloodGuard Dashboard - Hardware AP Mode</title>
  <style>
    :root {
      --bg: #0b132b;
      --card-bg: rgba(28, 37, 65, 0.7);
      --border: rgba(255, 255, 255, 0.1);
      --text: #ffffff;
      --text-muted: #94a3b8;
      --accent: #3a86ff;
      --green: #10b981;
      --yellow: #f59e0b;
      --red: #ef4444;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    body { background: var(--bg); color: var(--text); padding: 20px; min-height: 100vh; }
    .container { max-width: 900px; margin: 0 auto; }
    header { text-align: center; margin-bottom: 24px; }
    header h1 { font-size: 1.8rem; font-weight: 700; color: #38bdf8; letter-spacing: 1px; }
    header p { color: var(--text-muted); font-size: 0.9rem; margin-top: 4px; }
    .network-badge { display: inline-block; background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 999px; padding: 4px 12px; font-size: 0.75rem; font-weight: 600; margin-top: 8px; }
    
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-bottom: 20px; }
    .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 14px; padding: 18px; backdrop-filter: blur(10px); }
    .card-title { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); margin-bottom: 12px; }
    .card-value { font-size: 1.8rem; font-weight: 700; margin-bottom: 6px; }
    
    .progress-bar-bg { width: 100%; height: 12px; background: rgba(255,255,255,0.1); border-radius: 6px; overflow: hidden; margin-top: 8px; }
    .progress-bar { height: 100%; width: 0%; background: var(--green); transition: width 0.4s ease, background 0.4s ease; }
    
    .status-badge { display: inline-block; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 0.85rem; }
    .badge-normal   { background: rgba(16, 185, 129, 0.2); color: var(--green); border: 1px solid var(--green); }
    .badge-warning  { background: rgba(245, 158, 11, 0.2); color: var(--yellow); border: 1px solid var(--yellow); }
    .badge-danger   { background: rgba(239, 68, 68, 0.2); color: var(--red); border: 1px solid var(--red); }
    .badge-critical { background: var(--red); color: white; animation: pulse 1s infinite alternate; }
    
    @keyframes pulse { from { opacity: 0.7; } to { opacity: 1; } }

    .control-btn { background: #1e293b; color: white; border: 1px solid var(--border); padding: 10px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.2s; margin-right: 8px; margin-top: 8px; font-size: 0.85rem; }
    .control-btn:hover { background: #334155; transform: translateY(-1px); }
    .control-btn-primary { background: #2563eb; border-color: #3b82f6; }
    .control-btn-primary:hover { background: #1d4ed8; }
    .control-btn-danger  { background: #dc2626; border-color: #ef4444; }
    .control-btn-danger:hover  { background: #b91c1c; }
    .control-btn-valve { background: #0f766e; border-color: #14b8a6; }
    .control-btn-valve:hover { background: #0d9488; }
    .btn-valve-active { border: 2px solid #38bdf8 !important; background: #0284c7 !important; box-shadow: 0 0 10px rgba(56, 189, 248, 0.5); }
    .control-btn.disabled-btn { opacity: 0.45; cursor: not-allowed; }
    .control-btn.disabled-btn:hover { transform: none; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>FLOODGUARD DASHBOARD</h1>
      <p>Hệ Thống Chống Ngập Thông Minh (ESP32 Hardware AP Mode)</p>
      <div class="network-badge">Wi-Fi: FloodGuard_AP | IP: 192.168.4.1</div>
    </header>

    <div class="grid">
      <!-- Mực nước -->
      <div class="card">
        <div class="card-title">Mực Nước Hồ Thu</div>
        <div class="card-value" id="waterVal">0%</div>
        <div style="font-size: 0.85rem; color: var(--text-muted);">Khoảng cách: <span id="distVal">--</span> cm <span style="font-size: 0.75rem; color: #64748b;">(Đáy: 10cm | Đỉnh: 2cm)</span></div>
        <div style="font-size: 0.85rem; color: #38bdf8; margin-top: 4px;">Cột nước từ đáy: <span id="heightVal" style="font-weight: 700;">--</span> cm</div>
        <div class="progress-bar-bg">
          <div class="progress-bar" id="waterBar"></div>
        </div>
      </div>

      <!-- Trạng thái hệ thống -->
      <div class="card">
        <div class="card-title">Cảnh Báo & Chế Độ</div>
        <div style="margin-bottom: 10px;">
          <span id="stateBadge" class="status-badge badge-normal">NORMAL</span>
        </div>
        <div style="font-size: 0.85rem; color: var(--text-muted);">Chế độ: <span id="modeBadge" class="status-badge">AUTO</span></div>
        <div style="margin-top: 10px; font-size: 0.85rem; color: var(--text-muted);">
          Thời tiết: <span id="rainVal" style="font-weight: 600;">--</span> (ADC: <span id="rainAdcVal">--</span>)
        </div>
      </div>

      <!-- Thiết bị chấp hành -->
      <div class="card">
        <div class="card-title">Trạng Thái Thiết Bị</div>
        <div style="font-size: 0.9rem; margin-bottom: 6px;">Máy bơm 5V: <span id="pumpVal" style="font-weight: 700;">--</span></div>
        <div style="font-size: 0.9rem; margin-bottom: 6px;">Van xả nước: <span id="valveVal" style="font-weight: 700;">--</span></div>
        <div style="font-size: 0.9rem;">Còi báo động: <span id="buzzerVal" style="font-weight: 700;">--</span></div>
      </div>
    </div>

    <!-- Cụm điều khiển ảo -->
    <div class="card">
      <div class="card-title">Bảng Điều Khiển Can Thiệp (Manual / Auto Control)</div>
      <div id="modeStatusText" style="font-size: 0.85rem; margin-bottom: 12px; font-weight: 600;">
        <span style="color: #10b981;">🤖 Chế độ: AUTO</span> (Bơm & Van tự động. Bấm nút bất kỳ để can thiệp thủ công)
      </div>
      <div>
        <button class="control-btn control-btn-primary" id="btnMode" onclick="sendCommand('mode_toggle')">Đổi Chế Độ (AUTO / MANUAL)</button>
        <button class="control-btn" id="btnWebPump" onclick="sendCommand('pump_toggle')">Bật/Tắt Bơm (Manual)</button>
        <button class="control-btn control-btn-valve" id="btnValveCycle" onclick="sendCommand('valve_cycle')">Đổi Chế Độ Van (0% ➔ 50% ➔ 100%)</button>
      </div>
      <div style="margin-top: 10px; display: flex; align-items: center; flex-wrap: wrap;">
        <span style="font-size: 0.8rem; color: var(--text-muted); margin-right: 8px;">Góc mở trực tiếp:</span>
        <button class="control-btn" id="btnValve0" onclick="sendCommand('valve_0')">Van 0% (Đóng)</button>
        <button class="control-btn" id="btnValve50" onclick="sendCommand('valve_50')">Van 50% (Mở Nửa)</button>
        <button class="control-btn control-btn-danger" id="btnValve100" onclick="sendCommand('valve_100')">Van 100% (Mở Hết)</button>
      </div>
      <div id="manualWarning" style="margin-top: 10px; font-size: 0.8rem; color: #f59e0b; display: block;">
        💡 Ghi chú: Khi ở MANUAL, bạn tự do kiểm soát Bơm & Van. Đèn LED và Còi cảnh báo vẫn tự động hoạt động theo mực nước thực tế.
      </div>
    </div>
  </div>

  <script>
    async function updateStatus() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();

        document.getElementById('waterVal').innerText = data.water + '%';
        document.getElementById('distVal').innerText = data.distance;
        let h = (10.0 - data.distance).toFixed(1);
        if (h < 0) h = '0.0';
        const hElem = document.getElementById('heightVal');
        if (hElem) hElem.innerText = h;
        
        const bar = document.getElementById('waterBar');
        bar.style.width = data.water + '%';
        bar.style.background = data.water < 19 ? 'var(--green)' :
                               data.water < 38 ? 'var(--yellow)' : 'var(--red)';

        const sBadge = document.getElementById('stateBadge');
        sBadge.innerText = data.state;
        sBadge.className = 'status-badge ' + (
          data.state === 'NORMAL'   ? 'badge-normal'  :
          data.state === 'WARNING'  ? 'badge-warning' :
          data.state === 'DANGER'   ? 'badge-danger'  : 'badge-critical'
        );

        let rainText = 'KHONG MUA';
        let rainColor = '#94a3b8';
        if (data.rain_adc < 1100) {
          rainText = 'NGAP / MUA CUC TO !';
          rainColor = '#ef4444';
        } else if (data.rain_adc < 1800) {
          rainText = 'MUA TO !';
          rainColor = '#f59e0b';
        } else if (data.rain) {
          rainText = 'MUA NHO';
          rainColor = '#38bdf8';
        }
        document.getElementById('rainVal').innerText = rainText;
        document.getElementById('rainVal').style.color = rainColor;
        document.getElementById('rainAdcVal').innerText = data.rain_adc;

        const isManual = (data.mode === 'MANUAL');
        const mBadge = document.getElementById('modeBadge');
        mBadge.innerText = data.mode;
        mBadge.className = 'status-badge ' + (isManual ? 'badge-warning' : 'badge-normal');

        const btnMode = document.getElementById('btnMode');
        if (btnMode) {
          btnMode.innerText = isManual ? '⚙️ Chế Độ: MANUAL (Bấm chuyển AUTO)' : '🤖 Chế Độ: AUTO (Bấm chuyển MANUAL)';
        }

        const modeStatusText = document.getElementById('modeStatusText');
        if (modeStatusText) {
          modeStatusText.innerHTML = isManual ?
            '<span style="color: #f59e0b;">⚙️ Đang ở MANUAL:</span> Bơm & Van do bạn điều khiển. Đèn & Còi tự động cảnh báo theo mực nước.' :
            '<span style="color: #10b981;">🤖 Đang ở AUTO:</span> Bơm & Van tự động theo mực nước. Bấm nút bất kỳ để can thiệp thủ công.';
        }

        const pVal = document.getElementById('pumpVal');
        pVal.innerText = data.pump ? 'DANG BAT (ON)' : 'DA TAT (OFF)';
        pVal.style.color = data.pump ? '#10b981' : '#f87171';

        const btnPump = document.getElementById('btnWebPump');
        if (btnPump) {
          btnPump.innerText = data.pump ? '⚡ Tắt Bơm (Đang BẬT)' : '⚡ Bật Bơm (Đang TẮT)';
          btnPump.style.background = data.pump ? '#059669' : '#1e293b';
        }

        document.getElementById('valveVal').innerText = data.valve + '%';

        const btnValveCycle = document.getElementById('btnValveCycle');
        if (btnValveCycle) {
          if (data.valve === 0) btnValveCycle.innerText = '🎛️ Van: ĐANG ĐÓNG 0° (Bấm mở 50%)';
          else if (data.valve === 50) btnValveCycle.innerText = '🎛️ Van: ĐANG MỞ 90° (Bấm mở 100%)';
          else btnValveCycle.innerText = '🎛️ Van: ĐANG MỞ 180° (Bấm đóng 0%)';
        }

        const v0 = document.getElementById('btnValve0');
        const v50 = document.getElementById('btnValve50');
        const v100 = document.getElementById('btnValve100');
        if (v0 && v50 && v100) {
          v0.classList.toggle('btn-valve-active', data.valve === 0);
          v50.classList.toggle('btn-valve-active', data.valve === 50);
          v100.classList.toggle('btn-valve-active', data.valve === 100);
        }

        const bVal = document.getElementById('buzzerVal');
        if (data.state === 'CRITICAL' || data.buzzer === 'CONTINUOUS') {
          bVal.innerText = 'HU LIEN TUC';
          bVal.style.color = '#ef4444';
        } else if (data.state === 'DANGER' || data.buzzer === 'FAST') {
          bVal.innerText = 'DON DAP';
          bVal.style.color = '#f97316';
        } else if (data.state === 'WARNING' || data.buzzer === 'SLOW') {
          bVal.innerText = 'BAO NHE (BIP THUA)';
          bVal.style.color = '#f59e0b';
        } else {
          bVal.innerText = 'YEN LANG (TAT)';
          bVal.style.color = '#94a3b8';
        }
      } catch (err) {
        console.error('Loi cap nhat status:', err);
      }
    }

    async function sendCommand(cmd) {
      try {
        await fetch('/api/control?action=' + cmd);
        await updateStatus();
      } catch (err) {
        console.error('Loi gui lenh:', err);
      }
    }

    setInterval(updateStatus, 1000);
    updateStatus();
  </script>
</body>
</html>
)rawliteral";

// ==========================================
// CÁC HÀM XỬ LÝ REQUEST CỦA WEB SERVER
// ==========================================
void handleRoot() {
  server.send_P(200, "text/html", HTML_DASHBOARD);
}

void handleStatusApi() {
  const char* stStr = "NORMAL";
  const char* bzStr = "OFF";
  if (sysState == STATE_WARNING) {
    stStr = "WARNING";
    bzStr = "SLOW";
  } else if (sysState == STATE_DANGER) {
    stStr = "DANGER";
    bzStr = "FAST";
  } else if (sysState == STATE_CRITICAL) {
    stStr = "CRITICAL";
    bzStr = "CONTINUOUS";
  }

  char json[256];
  snprintf(json, sizeof(json),
    "{\"water\":%d,\"distance\":%.1f,\"rain\":%s,\"rain_adc\":%d,\"state\":\"%s\",\"mode\":\"%s\",\"pump\":%s,\"valve\":%d,\"buzzer\":\"%s\"}",
    waterPercent,
    currentDistance,
    isRaining ? "true" : "false",
    rainRawADC,
    stStr,
    isAutoMode ? "AUTO" : "MANUAL",
    pumpState ? "true" : "false",
    valvePercent,
    bzStr
  );

  server.send(200, "application/json", json);
}

void handleControlApi() {
  if (server.hasArg("mode")) {
    String m = server.arg("mode");
    if (m == "auto") isAutoMode = true;
    else if (m == "manual") isAutoMode = false;
  }

  // Nếu gửi lệnh điều khiển trực tiếp Bơm -> Chuyển sang MANUAL để người dùng kiểm soát
  if (server.hasArg("pump")) {
    String p = server.arg("pump");
    isAutoMode = false;
    if (p == "1" || p == "on") pumpState = true;
    else if (p == "0" || p == "off") pumpState = false;
    else if (p == "toggle") pumpState = !pumpState;
  }

  // Nếu gửi lệnh điều khiển trực tiếp Van -> Chuyển sang MANUAL để người dùng kiểm soát
  if (server.hasArg("valve")) {
    String v = server.arg("valve");
    isAutoMode = false;
    if (v == "toggle" || v == "cycle") {
      if (valvePercent == 0) valvePercent = 50;
      else if (valvePercent == 50) valvePercent = 100;
      else valvePercent = 0;
    } else {
      int val = v.toInt();
      if (val == 90) val = 50;
      else if (val == 180) val = 100;
      valvePercent = constrain(val, 0, 100);
    }
  }

  // 2. Tiếp nhận tham số hành động (Web Dashboard UI Buttons)
  if (server.hasArg("action")) {
    String act = server.arg("action");
    if (act == "mode_toggle") {
      isAutoMode = !isAutoMode;
    } else if (act == "mode_auto") {
      isAutoMode = true;
    } else if (act == "mode_manual") {
      isAutoMode = false;
    } else if (act == "pump_toggle") {
      isAutoMode = false;
      pumpState = !pumpState;
    } else if (act == "valve_cycle" || act == "valve_toggle" || act == "valve_mode") {
      isAutoMode = false;
      if (valvePercent == 0) valvePercent = 50;
      else if (valvePercent == 50) valvePercent = 100;
      else valvePercent = 0;
    } else if (act == "valve_0") {
      isAutoMode = false;
      valvePercent = 0;
    } else if (act == "valve_50") {
      isAutoMode = false;
      valvePercent = 50;
    } else if (act == "valve_100") {
      isAutoMode = false;
      valvePercent = 100;
    }
  }
  applyOutputs();
  server.send(200, "text/plain", "OK");
}

// ==========================================
// SETUP & LOOP
// ==========================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n==========================================");
  Serial.println("FLOODGUARD - CHE DO ACCESS POINT (HARDWARE)");
  Serial.println("==========================================");

  // Khởi tạo GPIO cảm biến
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_RAIN_DO, INPUT);   // Cảm biến mưa chân Digital (Input-only GPIO 34)
  pinMode(PIN_RAIN_ADC, INPUT);  // Cảm biến mưa chân Analog  (Input-only GPIO 35)

  // [KỸ THUẬT 1] Relay: Khởi động ở High-Z (INPUT)
  // Đảm bảo bơm TẮT hoàn toàn khi boot, tránh GPIO floating kích relay
  pinMode(PIN_RELAY, INPUT);

  // Khởi tạo GPIO đầu ra
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_YELLOW, OUTPUT);
  pinMode(PIN_LED_RED, OUTPUT);

  digitalWrite(PIN_LED_GREEN, LOW);
  digitalWrite(PIN_LED_YELLOW, LOW);
  digitalWrite(PIN_LED_RED, LOW);
  digitalWrite(PIN_BUZZER, LOW);

  // Khởi tạo Servo van xả (Cấu hình chuẩn ESP32Servo để không bị xung đột Timer với tone buzzer)
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  valveServo.setPeriodHertz(50); // Tần số 50Hz chuẩn cho servo SG90
  valveServo.attach(PIN_SERVO, 500, 2400);
  valveServo.write(0);

  // Khởi tạo Wi-Fi SoftAP (ESP32 tự phát sóng)
  WiFi.mode(WIFI_AP);
  bool apSuccess = WiFi.softAP(AP_SSID, AP_PASS);

  if (apSuccess) {
    IPAddress myIP = WiFi.softAPIP();
    Serial.println("[Wi-Fi] ESP32 da phat mang Wi-Fi thanh cong!");
    Serial.printf("[Wi-Fi] Ten mang (SSID): %s\n", AP_SSID);
    Serial.printf("[Wi-Fi] Mat khau (PASS) : %s\n", AP_PASS);
    Serial.printf("[Wi-Fi] Dia chi IP Web : http://%s\n", myIP.toString().c_str());
  } else {
    Serial.println("[Wi-Fi] Khoi tao SoftAP that bai!");
  }

  // Khởi tạo tên miền mDNS (http://floodguard.local)
  if (MDNS.begin("floodguard")) {
    Serial.println("[mDNS] Truy cap bang ten mien: http://floodguard.local");
  }

  // Khởi tạo Web Server
  server.on("/", handleRoot);
  server.on("/api/status", handleStatusApi);
  server.on("/api/control", handleControlApi);
  server.begin();
  Serial.println("[HTTP] Web Server da san sang tren cong 80.");
  Serial.println("==========================================\n");
}

void loop() {
  // [KỸ THUẬT 3] Toàn bộ non-blocking - không có delay() chặn luồng

  // 1. Phục vụ yêu cầu Web Server
  server.handleClient();

  unsigned long now = millis();

  // 2. Chu kỳ đọc cảm biến và đánh giá FSM (mỗi 150ms)
  //    Tăng lên 150ms vì readUltrasonicCM() mất ~36ms (3 mẫu x 12ms)
  if (now - lastSensorRead >= 150) {
    lastSensorRead = now;
    updateSensors();
    evaluateSystemStateAuto();
  }

  // 3. Cập nhật thiết bị chấp hành, LED và nhịp còi (non-blocking)
  applyOutputs();
}
