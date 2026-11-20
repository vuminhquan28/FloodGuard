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
// THÔNG SỐ ĐO VÀ NGƯỠNG MỰC NƯỚC (PHẦN CỨNG THẬT BỂ DEMO)
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
const int RAIN_ADC_LIGHT       = 2800; // Mưa nhỏ / vài giọt
const int RAIN_ADC_HEAVY       = 1800; // Mưa to / nhúng 1 phần
const int RAIN_ADC_SUBMERGED   = 1100; // Ngập hoàn toàn trong nước

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
unsigned long lastDebugPrint   = 0;

// ==========================================
// [THUẬT TOÁN CHỐNG RUNG GIẬT ĐA TẦNG]
// 1. Debounce thời gian chuyển trạng thái FSM (1.0 giây)
// 2. Thời gian chạy tối thiểu của máy bơm (5.0 giây)
// 3. Slew-rate Limiter điều khiển góc Servo SG90 mượt mà (mỗi 20ms quay 5 độ)
// 4. Failsafe Timeout (30s) & Safety Priority Override (10s ở CRITICAL)
// ==========================================
SystemState candidateState = STATE_NORMAL;
unsigned long candidateStartTime = 0;
const unsigned long DEBOUNCE_TIME_MS = 1000; // 1.0 giây

unsigned long pumpStartTime = 0;
const unsigned long PUMP_MIN_RUN_MS  = 5000; // 5.0 giây

unsigned long lastClientRequest      = 0;    // Heartbeat kết nối Web Dashboard
unsigned long critManualStartTime    = 0;    // Đếm thời gian ở CRITICAL trong Manual mode

// Biến quản lý góc xoay Servo mượt mà (Slew-rate Limiter)
static int servoActualAngle          = 0;
static unsigned long lastServoStepTime = 0;

// ==========================================
// [KỸ THUẬT 1] ĐỌC CẢM BIẾN - MEDIAN FILTER 3 MẪU
// Chống nhiễu EMI từ Relay/Motor bơm
// ==========================================
float readUltrasonicSingleCM() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  long duration = pulseIn(PIN_ECHO, HIGH, 30000); // Timeout 30ms (~5m)
  if (duration <= 0) return -1.0f;

  float dist = (duration * 0.0343f) / 2.0f;
  if (dist < 2.0f || dist > 300.0f) return -1.0f;
  return dist;
}

float readUltrasonicCM() {
  float samples[3];
  int validCount = 0;

  for (int i = 0; i < 3; i++) {
    samples[i] = readUltrasonicSingleCM();
    if (samples[i] > 0) validCount++;
    if (i < 2) delay(12); // Khoảng cách giữa các lần phát xung (10-15ms)
  }

  if (validCount == 0) return lastValidDistance;

  // Sắp xếp mẫu
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
    for (int i = 0; i < 3; i++) { if (samples[i] > 0) { result = samples[i]; break; } }
  } else if (validCount == 2) {
    float sum = 0; int cnt = 0;
    for (int i = 0; i < 3; i++) { if (samples[i] > 0) { sum += samples[i]; cnt++; } }
    result = sum / cnt;
  } else {
    result = samples[1]; // Median
  }

  lastValidDistance = result;
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

  // Đọc cảm biến mưa
  rainRawADC = analogRead(PIN_RAIN_ADC);
  bool rainDO = (digitalRead(PIN_RAIN_DO) == LOW);
  isRaining = rainDO || (rainRawADC < RAIN_ADC_LIGHT);

  // [DEBUG] In ra Serial Monitor mỗi 1 giây
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
// [THUẬT TOÁN FSM + HYSTERESIS + TIME DEBOUNCE 1.0S]
// Triệt tiêu hoàn toàn rung giật trạng thái và bảo vệ thiết bị
// ==========================================
void evaluateSystemStateAuto() {
  unsigned long now = millis();

  // 1. Phân loại mức mưa
  bool isLightRain = isRaining;                         // ADC < 2800 hoặc DO == LOW (Mưa nhỏ)
  bool isHeavyRain = (rainRawADC < RAIN_ADC_HEAVY);     // ADC < 1800 (Mưa to / nhúng 1 phần)
  bool isSubmerged = (rainRawADC < RAIN_ADC_SUBMERGED); // ADC < 1100 (Nhúng ngập hết vào nước / mưa xối xả)

  // 2. Xác định trạng thái đích mục tiêu (Target State) theo luật dải trễ Hysteresis
  SystemState targetState = sysState;
  switch (sysState) {
    case STATE_NORMAL:
      if (waterPercent >= THRESHOLD_CRIT_ENTER || isSubmerged) {
        targetState = STATE_CRITICAL;
      } else if (waterPercent >= THRESHOLD_DANGER_ENTER || isHeavyRain || (isLightRain && waterPercent >= THRESHOLD_WARN_ENTER)) {
        targetState = STATE_DANGER;
      } else if (waterPercent >= THRESHOLD_WARN_ENTER || isLightRain) {
        targetState = STATE_WARNING;
      }
      break;

    case STATE_WARNING:
      if (waterPercent >= THRESHOLD_CRIT_ENTER || isSubmerged) {
        targetState = STATE_CRITICAL;
      } else if (waterPercent >= THRESHOLD_DANGER_ENTER || isHeavyRain || (isLightRain && waterPercent >= THRESHOLD_DANGER_ENTER)) {
        targetState = STATE_DANGER;
      } else if (waterPercent < THRESHOLD_WARN_EXIT && !isLightRain) {
        targetState = STATE_NORMAL;
      }
      break;

    case STATE_DANGER:
      if (waterPercent >= THRESHOLD_CRIT_ENTER || isSubmerged || (isHeavyRain && waterPercent >= THRESHOLD_DANGER_ENTER)) {
        targetState = STATE_CRITICAL;
      } else if (waterPercent < THRESHOLD_DANGER_EXIT && !isHeavyRain) {
        targetState = STATE_WARNING;
      }
      break;

    case STATE_CRITICAL:
      if (waterPercent < THRESHOLD_CRIT_EXIT && !isSubmerged) {
        targetState = STATE_DANGER;
      }
      break;
  }

  // 3. Bộ lọc chống rung thời gian chuyển trạng thái (Debounce 1.0s)
  if (targetState != sysState) {
    // Nếu chuyển sang CRITICAL (khẩn cấp cứu hộ, chống tràn vỡ hồ): Phản ứng tức thời WCRT <= 250ms
    if (targetState == STATE_CRITICAL) {
      sysState = targetState;
      candidateState = sysState;
      candidateStartTime = 0;
    } else {
      // Chuyển trạng thái bậc thang thông thường: Duy trì liên tục tối thiểu DEBOUNCE_TIME_MS (1.0s)
      if (candidateState != targetState) {
        candidateState = targetState;
        candidateStartTime = now;
      } else if (now - candidateStartTime >= DEBOUNCE_TIME_MS) {
        sysState = candidateState;
        candidateStartTime = 0;
      }
    }
  } else {
    // Trạng thái mục tiêu trùng với hiện tại -> reset bộ đếm debounce
    candidateState = sysState;
    candidateStartTime = 0;
  }

  // 4. Điều khiển Bơm và Van theo trạng thái FSM (CHỈ KHI Ở CHẾ ĐỘ AUTO)
  if (isAutoMode) {
    switch (sysState) {
      case STATE_NORMAL:
      case STATE_WARNING:
        // Ràng buộc thời gian chạy tối thiểu của máy bơm (Min-run Time 5.0s)
        if (pumpState) {
          if (now - pumpStartTime >= PUMP_MIN_RUN_MS) {
            pumpState = false;
          }
        }
        valvePercent = 0;    // Van đóng hoàn toàn 0°
        break;

      case STATE_DANGER:
        if (!pumpState) {
          pumpState = true;
          pumpStartTime = now; // Ghi nhận thời điểm bắt đầu bật bơm
        }
        valvePercent = 50;   // Mở van thoát lũ 50% (90°)
        break;

      case STATE_CRITICAL:
        if (!pumpState) {
          pumpState = true;
          pumpStartTime = now;
        }
        valvePercent = 100;  // Mở van thoát lũ tối đa 100% (180°)
        break;
    }
  } else {
    // KHI Ở MANUAL MODE:
    // A. Failsafe Timeout 30 giây mất kết nối Web Dashboard -> Tự động khôi phục AUTO
    if (lastClientRequest > 0 && (now - lastClientRequest > 30000)) {
      isAutoMode = true;
      Serial.println("\n[FAILSAFE] Mat ket noi Web qua 30 giay -> Tu dong khoi phuc che do AUTO!");
    }

    // B. Safety Priority Override: Nếu ở mức CRITICAL quá 10 giây trong Manual -> Cưỡng chế chuyển AUTO
    if (sysState == STATE_CRITICAL) {
      if (critManualStartTime == 0) {
        critManualStartTime = now;
      } else if (now - critManualStartTime >= 10000) {
        isAutoMode = true;
        pumpState = true;
        pumpStartTime = now;
        valvePercent = 100;
        critManualStartTime = 0;
        Serial.println("\n[SAFETY OVERRIDE] Canh bao CRITICAL duy tri qua 10s o Manual -> Cuong che chuyen AUTO!");
      }
    } else {
      critManualStartTime = 0;
    }
  }

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
// ÁP ĐẶT ĐẦU RA (ACTUATORS, SERVO SLEW-RATE & LEDS)
// ==========================================
void applyOutputs() {
  unsigned long now = millis();

  // 1. [KỸ THUẬT 1] Điều khiển Relay bằng High-Z (INPUT) khi tắt bơm
  if (pumpState) {
    pinMode(PIN_RELAY, OUTPUT);
    digitalWrite(PIN_RELAY, LOW);   // LOW -> opto kích -> Relay đóng -> Bơm BẬT
  } else {
    pinMode(PIN_RELAY, INPUT);      // High-Z -> triệt tiêu hoàn toàn dòng rò -> Bơm TẮT hoàn toàn
  }

  // 2. [KỸ THUẬT 2] Điều khiển Servo van xả với thuật toán làm mượt chống rung giật (Soft PWM Stepping)
  int targetAngle = map(valvePercent, 0, 100, 0, 180);
  targetAngle = constrain(targetAngle, 0, 180);

  // Nội suy góc mượt mà: mỗi 20ms chỉ quay 5° hướng tới targetAngle
  // Khi đã đạt vị trí (servoActualAngle == targetAngle), ngừng phát xung thay đổi
  // Tay quay giữ nguyên vị trí ổn định tuyệt đối khi mực nước chưa đổi mức cảnh báo.
  if (servoActualAngle != targetAngle) {
    if (now - lastServoStepTime >= 20) {
      lastServoStepTime = now;
      if (servoActualAngle < targetAngle) {
        servoActualAngle += 5;
        if (servoActualAngle > targetAngle) servoActualAngle = targetAngle;
      } else {
        servoActualAngle -= 5;
        if (servoActualAngle < targetAngle) servoActualAngle = targetAngle;
      }
      valveServo.write(servoActualAngle);
      if (servoActualAngle == targetAngle) {
        Serial.printf("[SERVO] Da den goc on dinh: %d do (Van %d%%)\n", targetAngle, valvePercent);
      }
    }
  }

  // 3. [KỸ THUẬT 3] Đèn LED & Còi Buzzer đa cấp độ - TỰ ĐỘNG THEO SYSSTATE Ở CẢ AUTO VÀ MANUAL
  // Còi Active Buzzer 5V: Dùng digitalWrite HIGH/LOW, KHÔNG dùng tone()/noTone()
  // để tránh xung đột kênh Timer LEDC với Servo PWM làm servo nhảy loạn xạ.
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
    .btn-valve-active { border: 2px solid #38bdf8 !important; background: #0284c7 !important; box-shadow: 0 0 10px rgba(56, 189, 248, 0.5); font-weight: 700; }
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
        let h = (data.height !== undefined) ? data.height.toFixed(1) : ((10.0 - data.distance).toFixed(1));
        if (parseFloat(h) < 0) h = '0.0';
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

        let rainText = 'KHÔNG MƯA';
        let rainColor = '#94a3b8';
        if (data.rain_adc < 1100) {
          rainText = 'NGẬP / MƯA CỰC TO !';
          rainColor = '#ef4444';
        } else if (data.rain_adc < 1800) {
          rainText = 'MƯA TO !';
          rainColor = '#f59e0b';
        } else if (data.rain) {
          rainText = 'MƯA NHỎ';
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
        pVal.innerText = data.pump ? 'ĐANG BẬT (ON)' : 'ĐÃ TẮT (OFF)';
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
          bVal.innerText = 'HÚ LIÊN TỤC';
          bVal.style.color = '#ef4444';
        } else if (data.state === 'DANGER' || data.buzzer === 'FAST') {
          bVal.innerText = 'DỒN DẬP';
          bVal.style.color = '#f97316';
        } else if (data.state === 'WARNING' || data.buzzer === 'SLOW') {
          bVal.innerText = 'BÁO NHẸ (BÍP THƯA)';
          bVal.style.color = '#f59e0b';
        } else {
          bVal.innerText = 'YÊN LẶNG (TẮT)';
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
// CÁC HÀM XỬ LÝ REST API CỦA WEB SERVER
// ==========================================
void handleRoot() {
  server.send_P(200, "text/html", HTML_DASHBOARD);
}

void handleStatusApi() {
  lastClientRequest = millis(); // Cập nhật heartbeat kết nối

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

  float waterHeight = DISTANCE_EMPTY - currentDistance;
  if (waterHeight < 0.0f) waterHeight = 0.0f;

  char json[280];
  snprintf(json, sizeof(json),
    "{\"water\":%d,\"distance\":%.1f,\"height\":%.1f,\"rain\":%s,\"rain_adc\":%d,\"state\":\"%s\",\"mode\":\"%s\",\"pump\":%s,\"valve\":%d,\"buzzer\":\"%s\"}",
    waterPercent,
    currentDistance,
    waterHeight,
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
  lastClientRequest = millis(); // Cập nhật heartbeat kết nối

  // 1. Tham số tường minh
  if (server.hasArg("mode")) {
    String m = server.arg("mode");
    if (m == "auto") isAutoMode = true;
    else if (m == "manual") isAutoMode = false;
  }

  // Can thiệp Bơm trực tiếp -> tự động chuyển sang MANUAL
  if (server.hasArg("pump")) {
    String p = server.arg("pump");
    isAutoMode = false;
    if (p == "1" || p == "on") {
      pumpState = true;
      pumpStartTime = millis();
    } else if (p == "0" || p == "off") {
      pumpState = false;
    } else if (p == "toggle") {
      pumpState = !pumpState;
      if (pumpState) pumpStartTime = millis();
    }
  }

  // Can thiệp Van trực tiếp -> tự động chuyển sang MANUAL
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

  // 2. Tham số hành động nút bấm Web Dashboard (UI Buttons)
  if (server.hasArg("action")) {
    String act = server.arg("action");
    if (act == "mode_toggle") {
      isAutoMode = !isAutoMode;
    } else if (act == "mode_auto") {
      isAutoMode = true;
    } else if (act == "mode_manual") {
      isAutoMode = false;
    } else if (act == "pump_toggle") {
      isAutoMode = false; // Seamless transition
      pumpState = !pumpState;
      if (pumpState) pumpStartTime = millis();
    } else if (act == "valve_cycle" || act == "valve_toggle" || act == "valve_mode") {
      isAutoMode = false; // Seamless transition
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

  // Phản hồi phần cứng ngay lập tức
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
  Serial.println("DEMO TANK 10CM - HE THONG CHONG RUNG GIAT DA TANG");
  Serial.println("==========================================");

  // Khởi tạo GPIO cảm biến
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_RAIN_DO, INPUT);   // Cảm biến mưa Digital (GPIO 34)
  pinMode(PIN_RAIN_ADC, INPUT);  // Cảm biến mưa Analog  (GPIO 35)

  // [KỸ THUẬT 1] Relay: Khởi động ở High-Z (INPUT) để tránh GPIO floating kích relay khi boot
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

  // Khởi tạo Servo van xả với ESP32PWM allocateTimer
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  valveServo.setPeriodHertz(50); // 50Hz chuẩn cho SG90
  valveServo.attach(PIN_SERVO, 500, 2400);
  valveServo.write(0);
  servoActualAngle = 0;

  // Khởi tạo Wi-Fi SoftAP
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

  // Khởi tạo mDNS (http://floodguard.local)
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
  // 1. Phục vụ yêu cầu Web Server
  server.handleClient();

  unsigned long now = millis();

  // 2. Chu kỳ đọc cảm biến và đánh giá FSM (mỗi 150ms)
  if (now - lastSensorRead >= 150) {
    lastSensorRead = now;
    updateSensors();
    evaluateSystemStateAuto();
  }

  // 3. Cập nhật thiết bị chấp hành, Slew-rate Servo và nhịp còi (non-blocking)
  applyOutputs();
}
