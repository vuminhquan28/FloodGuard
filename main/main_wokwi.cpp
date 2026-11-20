#include <Arduino.h>
#include <ESP32Servo.h>
#include <WiFi.h>
#include <WebServer.h>

// ==========================================
// CẤU HÌNH CHÂN CẮM (THEO DIAGRAM.JSON - WOKWI SIMULATION)
// Đồng bộ 100% với sơ đồ nguyên lý phần cứng
// ==========================================
#define PIN_TRIG        13   // Cảm biến siêu âm Trig (GPIO 13)
#define PIN_ECHO        12   // Cảm biến siêu âm Echo (GPIO 12)
#define PIN_RAIN_ADC    35   // Chiết áp mô phỏng cảm biến mưa AO (GPIO 35 - ADC1_CH7)
#define PIN_SERVO       27   // Điều khiển van xả nước SG90 PWM (GPIO 27)
#define PIN_RELAY       23   // Điều khiển Relay máy bơm 5V (GPIO 23 - Active LOW)
#define PIN_BUZZER      4    // Còi báo động (GPIO 4)
#define PIN_LED_GREEN   21   // LED trạng thái NORMAL (GPIO 21)
#define PIN_LED_YELLOW  19   // LED trạng thái WARNING (GPIO 19)
#define PIN_LED_RED     18   // LED trạng thái DANGER / CRITICAL (GPIO 18)

// Logic kích hoạt Relay máy bơm (Wokwi module PNP: LOW = Đóng tiếp điểm BẬT bơm)
#define RELAY_ON        LOW
#define RELAY_OFF       HIGH

// ==========================================
// THÔNG SỐ ĐO VÀ NGƯỠNG MỰC NƯỚC (BỂ CHUẨN 50CM - WOKWI SIMULATION)
// Giữ nguyên dải đo khoảng cách ban đầu:
// 50cm = Đáy bể / Cạn hoàn toàn (0%)
// 5cm  = Đỉnh bể / Tràn đầy (100%)
// Cột nước từ đáy bể: h = DISTANCE_EMPTY - d = 50.0cm - d (0cm - 45cm)
// ==========================================
const float DISTANCE_EMPTY = 50.0;  // Khoảng cách đáy hồ khi cạn (cm) - 0%
const float DISTANCE_FULL  = 5.0;   // Khoảng cách mép đầy tràn (cm) - 100%

// Dải trễ (Hysteresis) FSM - Vào trạng thái mực nước
const int THRESHOLD_WARN_ENTER   = 21; // d <= 40.5cm (nước >= 21%)
const int THRESHOLD_DANGER_ENTER = 44; // d <= 30.2cm (nước >= 44%)
const int THRESHOLD_CRIT_ENTER   = 63; // d <= 21.6cm (nước >= 63%)

// Dải trễ (Hysteresis) FSM - Thoát trạng thái (khi nước rút, Delta = 3%)
const int THRESHOLD_CRIT_EXIT    = 60; // d > 23.0cm (nước < 60%)
const int THRESHOLD_DANGER_EXIT  = 41; // d > 31.5cm (nước < 41%)
const int THRESHOLD_WARN_EXIT    = 18; // d > 41.9cm (nước < 18%)

// Ngưỡng cảm biến mưa (Chiết áp / ADC 12-bit: 0 - 4095)
const int RAIN_ADC_LIGHT         = 2800; // Mưa nhỏ / ẩm ướt
const int RAIN_ADC_HEAVY         = 1800; // Mưa to / vặn chiết áp thấp
const int RAIN_ADC_SUBMERGED     = 1100; // Ngập hoàn toàn / vặn chiết áp sát 0

// Định nghĩa trạng thái hệ thống
enum SystemState {
  STATE_NORMAL,
  STATE_WARNING,
  STATE_DANGER,
  STATE_CRITICAL
};

// ==========================================
// THIẾT BỊ NGOẠI VI & BIẾN TOÀN CỤC
// ==========================================
Servo valveServo;
WebServer server(80);

SystemState sysState    = STATE_NORMAL;
float currentDistance   = 50.0;
int   waterPercent      = 0;
bool  isRaining         = false;
int   rainRawADC        = 0;

bool isAutoMode         = true;
bool pumpState          = false;
int  valvePercent       = 0;      // 0%, 50%, 100%

// Biến quản lý thời gian non-blocking
unsigned long lastSensorRead     = 0;
unsigned long lastClientRequest  = 0; // Heartbeat giám sát kết nối Web Client

// Prototype
void applyOutputs();

// ==========================================
// HÀM ĐỌC CẢM BIẾN
// ==========================================
float readUltrasonicCM() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  long duration = pulseIn(PIN_ECHO, HIGH, 30000); // Timeout 30ms (~5m)
  if (duration == 0) return currentDistance;     // Giữ giá trị trước nếu mất xung
  float d = duration * 0.0343 / 2.0;
  return constrain(d, DISTANCE_FULL, DISTANCE_EMPTY);
}

void updateSensors() {
  currentDistance = readUltrasonicCM();
  // Quy đổi khoảng cách sang % mực nước (càng gần đỉnh thì % càng cao)
  float rawPercent = (DISTANCE_EMPTY - currentDistance) / (DISTANCE_EMPTY - DISTANCE_FULL) * 100.0;
  waterPercent = (int)constrain(round(rawPercent), 0, 100);

  rainRawADC = analogRead(PIN_RAIN_ADC);
  isRaining = (rainRawADC < RAIN_ADC_LIGHT);

  // In thông số ra Serial Monitor mỗi 1 giây để theo dõi trực quan trên Wokwi
  static unsigned long lastSensorLog = 0;
  if (millis() - lastSensorLog >= 1000) {
    lastSensorLog = millis();
    const char* rainStr = (rainRawADC < RAIN_ADC_SUBMERGED) ? "NGAP_NUOC (CRIT)" :
                          (rainRawADC < RAIN_ADC_HEAVY)     ? "MUA_TO (DANGER)" :
                          (isRaining)                       ? "MUA_NHO (WARN)" : "KHO_RAO (NORMAL)";
    const char* stNames[] = {"NORMAL", "WARNING", "DANGER", "CRITICAL"};
    Serial.printf("[WOKWI TELEMETRY] Dist=%5.1fcm (%2d%%, cot nuoc %4.1fcm) | RainADC=%4d (%s) | FSM: %-8s (%s) | Bom: %s | Van: %3d%%\n",
      currentDistance, waterPercent, (DISTANCE_EMPTY - currentDistance), rainRawADC, rainStr,
      stNames[sysState], isAutoMode ? "AUTO" : "MANUAL",
      pumpState ? "BAT (ON) " : "TAT (OFF)", valvePercent);
  }
}

// ==========================================
// THUẬT TOÁN FSM & HYSTERESIS
// ==========================================
void evaluateSystemStateAuto() {
  bool isLightRain = isRaining;
  bool isHeavyRain = (rainRawADC < RAIN_ADC_HEAVY);
  bool isSubmerged = (rainRawADC < RAIN_ADC_SUBMERGED);

  // 1. Luôn tính toán sysState theo cảm biến để điều khiển Đèn LED & Còi (ở cả AUTO và MANUAL)
  switch (sysState) {
    case STATE_NORMAL:
      if (waterPercent >= THRESHOLD_CRIT_ENTER || isSubmerged) {
        sysState = STATE_CRITICAL;
      } else if (waterPercent >= THRESHOLD_DANGER_ENTER || isHeavyRain || (isLightRain && waterPercent >= THRESHOLD_WARN_ENTER)) {
        sysState = STATE_DANGER;
      } else if (waterPercent >= THRESHOLD_WARN_ENTER || isLightRain) {
        sysState = STATE_WARNING;
      }
      break;

    case STATE_WARNING:
      if (waterPercent >= THRESHOLD_CRIT_ENTER || isSubmerged) {
        sysState = STATE_CRITICAL;
      } else if (waterPercent >= THRESHOLD_DANGER_ENTER || isHeavyRain || (isLightRain && waterPercent >= THRESHOLD_DANGER_ENTER)) {
        sysState = STATE_DANGER;
      } else if (waterPercent < THRESHOLD_WARN_EXIT && !isLightRain) {
        sysState = STATE_NORMAL;
      }
      break;

    case STATE_DANGER:
      if (waterPercent >= THRESHOLD_CRIT_ENTER || isSubmerged || (isHeavyRain && waterPercent >= THRESHOLD_DANGER_ENTER)) {
        sysState = STATE_CRITICAL;
      } else if (waterPercent < THRESHOLD_DANGER_EXIT && !isHeavyRain) {
        sysState = STATE_WARNING;
      }
      break;

    case STATE_CRITICAL:
      if (waterPercent < THRESHOLD_CRIT_EXIT && !isSubmerged) {
        sysState = STATE_DANGER;
      }
      break;
  }

  // 2. Phân quyền điều khiển cơ cấu chấp hành (Máy bơm & Van xả)
  if (isAutoMode) {
    // CHẾ ĐỘ AUTO: FSM toàn quyền điều khiển Bơm và Van theo trạng thái
    switch (sysState) {
      case STATE_NORMAL:
      case STATE_WARNING:
        pumpState = false;
        valvePercent = 0;
        break;
      case STATE_DANGER:
        pumpState = (waterPercent >= 20); // Khóa an toàn chống cháy cạn nếu nước < 20%
        valvePercent = 50;
        break;
      case STATE_CRITICAL:
        pumpState = true;
        valvePercent = 100;
        break;
    }
  } else {
    // CHẾ ĐỘ MANUAL:
    // pumpState và valvePercent do người vận hành trực tiếp điều khiển qua Web Dashboard.
    // FSM tuyệt đối không can thiệp hay ghi đè lên Bơm và Van.
    // Đèn LED và Còi Buzzer vẫn tự động cảnh báo theo thời gian thực.

    // A. Cơ chế bảo vệ an toàn Failsafe Timeout 30s:
    // Nếu mất kết nối với Web Client quá 30 giây -> tự động hoàn nguyên về AUTO
    if (lastClientRequest > 0 && millis() - lastClientRequest > 30000) {
      isAutoMode = true;
      Serial.println("\n>>> [FAILSAFE] Khong nhan duoc tin hieu Web qua 30s! Tu dong hoan nguyen ve AUTO de an toan.\n");
    }

    // B. Cơ chế bảo vệ an toàn khẩn cấp Safety Priority Override 10s:
    // Nếu mức nước chạm ngưỡng CRITICAL kéo dài quá 10s mà van chưa mở 100% hoặc bơm chưa bật
    // -> Cưỡng chế bật bơm, mở van 100% và trả về AUTO để chống vỡ/tràn bể
    static unsigned long criticalStart = 0;
    if (sysState == STATE_CRITICAL && (valvePercent < 100 || !pumpState)) {
      if (criticalStart == 0) criticalStart = millis();
      else if (millis() - criticalStart >= 10000) {
        isAutoMode   = true;
        pumpState    = true;
        valvePercent = 100;
        Serial.println("\n>>> [SAFETY OVERRIDE] Muc nuoc CRITICAL > 10s o MANUAL! Cuong che bat bom & mo van 100% ve AUTO!\n");
        criticalStart = 0;
      }
    } else {
      criticalStart = 0;
    }
  }

  // Báo thay đổi trạng thái tức thời ra Serial Monitor
  static SystemState lastFsmState = (SystemState)99;
  if (sysState != lastFsmState) {
    const char* stNames[] = {"NORMAL", "WARNING", "DANGER", "CRITICAL"};
    Serial.printf("\n>>> [FSM CHUYEN TRANG THAI] %s (%s) | Nuoc: %d%% | RainADC: %d | Bom: %s | Van: %d%%\n\n",
      stNames[sysState], isAutoMode ? "AUTO" : "MANUAL", waterPercent, rainRawADC, pumpState ? "BAT" : "TAT", valvePercent);
    lastFsmState = sysState;
  }
}

// ==========================================
// XUẤT TÍN HIỆU NGOẠI VI (ACTUATORS, LEDS, BUZZER)
// ==========================================
void applyOutputs() {
  // 1. Điều khiển Rơ-le máy bơm (Active LOW)
  digitalWrite(PIN_RELAY, pumpState ? RELAY_ON : RELAY_OFF);

  // 2. Điều khiển Van xả Servo SG90 (0% = 0°, 50% = 90°, 100% = 180°)
  // Thuật toán Anti-Jitter: chỉ write xung khi góc mở thực sự thay đổi
  // Khi ở cùng mức cảnh báo, tay quay giữ nguyên vị trí ổn định tuyệt đối
  static int currentServoAngle = -1;
  int targetAngle = map(valvePercent, 0, 100, 0, 180);
  targetAngle = constrain(targetAngle, 0, 180);
  if (targetAngle != currentServoAngle) {
    valveServo.write(targetAngle);
    currentServoAngle = targetAngle;
    Serial.printf("[SERVO] Xoay goc: %d do (Van %d%%)\n", targetAngle, valvePercent);
  }

  // 3. Đèn LED & Còi Buzzer đa cấp độ - TỰ ĐỘNG THEO SYSSTATE Ở CẢ AUTO VÀ MANUAL
  unsigned long now = millis();
  switch (sysState) {
    case STATE_NORMAL:
      digitalWrite(PIN_LED_GREEN, HIGH);
      digitalWrite(PIN_LED_YELLOW, LOW);
      digitalWrite(PIN_LED_RED, LOW);
      noTone(PIN_BUZZER);
      digitalWrite(PIN_BUZZER, LOW);
      break;

    case STATE_WARNING:
      // Mức dâng cảnh báo: LED Vàng sáng, Còi bíp nhẹ ngắt quãng thưa (chu kỳ 1500ms, bíp 120ms)
      digitalWrite(PIN_LED_GREEN, LOW);
      digitalWrite(PIN_LED_YELLOW, HIGH);
      digitalWrite(PIN_LED_RED, LOW);
      if (now % 1500 < 120) {
        tone(PIN_BUZZER, 1000);
      } else {
        noTone(PIN_BUZZER);
        digitalWrite(PIN_BUZZER, LOW);
      }
      break;

    case STATE_DANGER:
      // Nguy cơ ngập: LED Đỏ sáng, Còi báo dồn dập (chu kỳ 300ms: kêu 150ms, tắt 150ms)
      digitalWrite(PIN_LED_GREEN, LOW);
      digitalWrite(PIN_LED_YELLOW, LOW);
      digitalWrite(PIN_LED_RED, HIGH);
      if (now % 300 < 150) {
        tone(PIN_BUZZER, 1800);
      } else {
        noTone(PIN_BUZZER);
        digitalWrite(PIN_BUZZER, LOW);
      }
      break;

    case STATE_CRITICAL:
      // Ngập nghiêm trọng: LED Đỏ chớp nháy dồn dập (chu kỳ 100ms), Còi hú liên tục không ngắt
      digitalWrite(PIN_LED_GREEN, LOW);
      digitalWrite(PIN_LED_YELLOW, LOW);
      digitalWrite(PIN_LED_RED, (now % 100 < 50) ? HIGH : LOW);
      tone(PIN_BUZZER, 2500);
      break;
  }
}

// ==========================================
// WEB SERVER TELEMETRY & DASHBOARD (DARK GLASSMORPHISM)
// ==========================================
const char HTML_DASHBOARD[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FloodGuard Dashboard - Wokwi Simulation</title>
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
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>FLOODGUARD DASHBOARD</h1>
      <p>Hệ Thống Chống Ngập Thông Minh (Wokwi Simulation Mode)</p>
      <div class="network-badge">⚡ Wokwi Virtual Network | Bể Chuẩn: 50cm - 5cm</div>
    </header>

    <div class="grid">
      <!-- Mực nước -->
      <div class="card">
        <div class="card-title">Mực Nước Hồ Thu</div>
        <div class="card-value" id="waterVal">0%</div>
        <div style="font-size: 0.85rem; color: var(--text-muted);">Khoảng cách: <span id="distVal">--</span> cm <span style="font-size: 0.75rem; color: #64748b;">(Đáy: 50cm | Đỉnh: 5cm)</span></div>
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
        <button class="control-btn" id="btnValve0" onclick="sendCommand('valve_0')">Van 0% (Đóng 0°)</button>
        <button class="control-btn" id="btnValve50" onclick="sendCommand('valve_50')">Van 50% (Mở 90°)</button>
        <button class="control-btn control-btn-danger" id="btnValve100" onclick="sendCommand('valve_100')">Van 100% (Mở 180°)</button>
      </div>
      <div id="manualWarning" style="margin-top: 10px; font-size: 0.8rem; color: #f59e0b; display: block;">
        💡 <i>Ở chế độ MANUAL: Đèn LED và Còi Buzzer vẫn tự động cảnh báo theo mực nước. Failsafe tự động trả về AUTO sau 30s nếu mất kết nối.</i>
      </div>
    </div>
  </div>

  <script>
    async function updateStatus() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();

        // 1. Mực nước
        document.getElementById('waterVal').innerText = data.water + '%';
        document.getElementById('distVal').innerText = data.distance.toFixed(1);
        const colHeight = (data.height !== undefined) ? data.height.toFixed(1) : (50.0 - data.distance).toFixed(1);
        document.getElementById('heightVal').innerText = colHeight;

        const bar = document.getElementById('waterBar');
        bar.style.width = data.water + '%';
        if (data.water < 21) {
          bar.style.background = 'var(--green)';
        } else if (data.water < 44) {
          bar.style.background = 'var(--yellow)';
        } else if (data.water < 63) {
          bar.style.background = 'var(--red)';
        } else {
          bar.style.background = '#dc2626';
        }

        // 2. Cảnh báo FSM
        const badge = document.getElementById('stateBadge');
        badge.innerText = data.state;
        badge.className = 'status-badge ' + (
          data.state === 'NORMAL'   ? 'badge-normal' :
          data.state === 'WARNING'  ? 'badge-warning' :
          data.state === 'DANGER'   ? 'badge-danger' : 'badge-critical'
        );

        // 3. Thời tiết
        let rText = 'KHÔ RÁO';
        let rColor = '#cbd5e1';
        if (data.rain_adc < 1100) {
          rText = 'NGẬP NƯỚC (CRITICAL)';
          rColor = '#ef4444';
        } else if (data.rain_adc < 1800) {
          rText = 'MƯA TO (DANGER)';
          rColor = '#f97316';
        } else if (data.rain_adc < 2800 || data.rain) {
          rText = 'MƯA NHỎ (WARNING)';
          rColor = '#38bdf8';
        }
        const rainEl = document.getElementById('rainVal');
        rainEl.innerText = rText;
        rainEl.style.color = rColor;
        document.getElementById('rainAdcVal').innerText = data.rain_adc;

        // 4. Chế độ vận hành
        const mBadge = document.getElementById('modeBadge');
        const isManual = (data.mode === 'MANUAL');
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

        // 5. Máy bơm
        const pVal = document.getElementById('pumpVal');
        pVal.innerText = data.pump ? 'ĐANG BẬT (ON)' : 'ĐÃ TẮT (OFF)';
        pVal.style.color = data.pump ? '#10b981' : '#f87171';

        const btnPump = document.getElementById('btnWebPump');
        if (btnPump) {
          btnPump.innerText = data.pump ? '⚡ Tắt Bơm (Đang BẬT)' : '⚡ Bật Bơm (Đang TẮT)';
          btnPump.style.background = data.pump ? '#059669' : '#1e293b';
        }

        // 6. Van xả
        const vAngle = Math.round(data.valve * 1.8);
        document.getElementById('valveVal').innerText = data.valve + '% (' + (data.valve === 0 ? 'Đóng 0°' : (data.valve === 50 ? 'Mở 90°' : 'Mở 180°')) + ')';

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

        // 7. Còi báo động
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
  if (waterHeight < 0) waterHeight = 0;

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
    if (p == "1" || p == "on") pumpState = true;
    else if (p == "0" || p == "off") pumpState = false;
    else if (p == "toggle") pumpState = !pumpState;
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
  Serial.println("\n==========================================");
  Serial.println("FLOODGUARD - WOKWI SIMULATION (STANDARD 50CM TANK)");
  Serial.println("==========================================");

  // Thiết lập chân GPIO
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_RAIN_ADC, INPUT);

  pinMode(PIN_RELAY, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_YELLOW, OUTPUT);
  pinMode(PIN_LED_RED, OUTPUT);

  digitalWrite(PIN_RELAY, RELAY_OFF); // Active LOW: HIGH = TẮT bơm khi khởi động
  digitalWrite(PIN_LED_GREEN, LOW);
  digitalWrite(PIN_LED_YELLOW, LOW);
  digitalWrite(PIN_LED_RED, LOW);
  noTone(PIN_BUZZER);

  // Khởi tạo Servo van xả nước
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  valveServo.setPeriodHertz(50);
  valveServo.attach(PIN_SERVO, 500, 2400);
  valveServo.write(0);

  // Khởi tạo Wi-Fi Wokwi
  Serial.print("Ket noi WiFi Wokwi-GUEST...");
  WiFi.begin("Wokwi-GUEST", "");
  int retry = 0;
  while (WiFi.status() != WL_CONNECTED && retry < 20) {
    delay(200);
    Serial.print(".");
    retry++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi da ket noi!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nChua ket noi duoc WiFi (chay offline).");
  }

  // Khởi tạo Web Server
  server.on("/", handleRoot);
  server.on("/api/status", handleStatusApi);
  server.on("/api/control", handleControlApi);
  server.begin();
  Serial.println("Web Server da san sang.");
  Serial.println("He thong san sang do luong va dieu khien!\n");
}

void loop() {
  // 1. Phục vụ yêu cầu Web Server
  server.handleClient();

  // 2. Chu kỳ đọc cảm biến và đánh giá logic FSM (mỗi 100ms)
  unsigned long now = millis();
  if (now - lastSensorRead >= 100) {
    lastSensorRead = now;
    updateSensors();
    evaluateSystemStateAuto();
  }

  // 3. Cập nhật thiết bị chấp hành, LED và nhịp còi liên tục (non-blocking)
  applyOutputs();

  delay(10);
}
