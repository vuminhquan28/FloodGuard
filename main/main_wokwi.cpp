#include <Arduino.h>
#include <ESP32Servo.h>
#include <WiFi.h>
#include <WebServer.h>

// ==========================================
// CẤU HÌNH CHÂN CẮM (THEO DIAGRAM.JSON - WOKWI SIMULATION)
// Đồng bộ với pinout phần cứng thực tế (main_hardware.cpp)
// ==========================================
#define PIN_TRIG        13   // Cảm biến siêu âm Trig
#define PIN_ECHO        12   // Cảm biến siêu âm Echo
#define PIN_RAIN_ADC    35   // Chiết áp mô phỏng cảm biến mưa (Analog AO)
#define PIN_SERVO       27   // Điều khiển van xả nước SG90
#define PIN_RELAY       23   // Điều khiển Relay máy bơm (Active LOW)
#define PIN_BUZZER      4    // Còi báo động
#define PIN_LED_GREEN   21   // LED trạng thái NORMAL
#define PIN_LED_YELLOW  19   // LED trạng thái WARNING
#define PIN_LED_RED     18   // LED trạng thái DANGER / CRITICAL

// Logic kích hoạt Relay máy bơm (Module Relay 1 kênh Active LOW)
#define RELAY_ON        LOW
#define RELAY_OFF       HIGH

// ==========================================
// THÔNG SỐ ĐO VÀ NGƯỠNG MỰC NƯỚC
// ==========================================
// Chiều sâu đo cảm biến siêu âm (cm):
// 50cm = Đáy bể / Cạn hoàn toàn (0%)
// 5cm  = Đỉnh bể / Tràn đầy (100%)
const float DISTANCE_EMPTY = 50.0;
const float DISTANCE_FULL  = 5.0;

// Ngưỡng cảm biến mưa (Chiết áp / ADC 12-bit: 0 - 4095)
const int RAIN_ADC_LIGHT      = 2800; // Mưa nhỏ / ẩm ướt
const int RAIN_ADC_HEAVY      = 1800; // Mưa to / vặn chiết áp thấp
const int RAIN_ADC_SUBMERGED  = 1100; // Ngập hoàn toàn / vặn chiết áp sát 0

// Định nghĩa trạng thái hệ thống
enum SystemState {
  STATE_NORMAL,
  STATE_WARNING,
  STATE_DANGER,
  STATE_CRITICAL
};

// ==========================================
// KHAI BÁO THIẾT BỊ NGOẠI VI
// ==========================================
Servo valveServo;
WebServer server(80);

// ==========================================
// BIẾN TRẠNG THÁI TOÀN CỤC
// ==========================================
float currentDistance = 50.0;
int   waterPercent    = 0;
bool  isRaining       = false;
int   rainRawADC      = 0;

bool isAutoMode       = true;
bool pumpState        = false;
int  valvePercent     = 0;      // 0%, 50%, 100%
SystemState sysState  = STATE_NORMAL;

// Biến điều khiển thời gian non-blocking
unsigned long lastSensorRead   = 0;
unsigned long lastBuzzerBlink  = 0;
bool buzzerToggle              = false;

// ==========================================
// HÀM ĐỌC CẢM BIẾN
// ==========================================
float readUltrasonicCM() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  long duration = pulseIn(PIN_ECHO, HIGH, 26000); // Timeout ~4.5m
  if (duration == 0) return currentDistance; // Giữ giá trị trước nếu mất xung
  float d = duration * 0.0343 / 2.0;
  return constrain(d, DISTANCE_FULL, DISTANCE_EMPTY);
}

void updateSensors() {
  currentDistance = readUltrasonicCM();
  // Quy đổi khoảng cách sang % mực nước (càng gần thì % càng cao)
  float rawPercent = (DISTANCE_EMPTY - currentDistance) / (DISTANCE_EMPTY - DISTANCE_FULL) * 100.0;
  waterPercent = (int)constrain(round(rawPercent), 0, 100);

  rainRawADC = analogRead(PIN_RAIN_ADC);
  isRaining = (rainRawADC < RAIN_ADC_LIGHT);
}

// ==========================================
// THUẬT TOÁN FSM & HYSTERESIS (UC03, UC04, UC05)
// ==========================================
void evaluateSystemStateAuto() {
  if (!isAutoMode) return;

  bool isLightRain = isRaining;
  bool isHeavyRain = (rainRawADC < RAIN_ADC_HEAVY);
  bool isSubmerged = (rainRawADC < RAIN_ADC_SUBMERGED);

  // Logic Hysteresis kết hợp mực nước và cấp độ mưa:
  switch (sysState) {
    case STATE_NORMAL:
      if (waterPercent >= 71 || isSubmerged) {
        sysState = STATE_CRITICAL;
      } else if (waterPercent >= 41 || isHeavyRain || (isLightRain && waterPercent >= 21)) {
        sysState = STATE_DANGER;
      } else if (waterPercent >= 21 || isLightRain) {
        sysState = STATE_WARNING;
      }
      break;

    case STATE_WARNING:
      if (waterPercent >= 71 || isSubmerged) {
        sysState = STATE_CRITICAL;
      } else if (waterPercent >= 41 || isHeavyRain || (isLightRain && waterPercent >= 30)) {
        sysState = STATE_DANGER;
      } else if (waterPercent < 20 && !isLightRain) {
        sysState = STATE_NORMAL;
      }
      break;

    case STATE_DANGER:
      if (waterPercent >= 71 || isSubmerged || (isHeavyRain && waterPercent >= 30)) {
        sysState = STATE_CRITICAL;
      } else if (waterPercent < 40 && !isHeavyRain) {
        sysState = STATE_WARNING;
      }
      break;

    case STATE_CRITICAL:
      if (waterPercent < 71 && !isSubmerged) {
        sysState = STATE_DANGER;
      }
      break;
  }

  // Tự động điều khiển Bơm và Van theo trạng thái FSM (AUTO)
  switch (sysState) {
    case STATE_NORMAL:
      pumpState = false;
      valvePercent = 0;
      break;
    case STATE_WARNING:
      pumpState = false;
      valvePercent = 0;
      break;
    case STATE_DANGER:
      pumpState = true;
      valvePercent = 50;
      break;
    case STATE_CRITICAL:
      pumpState = true;
      valvePercent = 100;
      break;
  }
}

// ==========================================
// XUẤT TÍN HIỆU NGOẠI VI (LED, RELAY, SERVO, BUZZER)
// ==========================================
void applyOutputs() {
  // 1. Điều khiển Bơm (Module Relay Active LOW: LOW = BẬT bơm, HIGH = TẮT bơm)
  // Wokwi: thêm attr "transistor":"pnp" vào relay trong diagram.json để mô phỏng đúng Active LOW
  digitalWrite(PIN_RELAY, pumpState ? RELAY_ON : RELAY_OFF);

  // 2. Điều khiển Van xả (Servo SG90: 0% -> 0 độ, 50% -> 90 độ, 100% -> 180 độ)
  int servoAngle = map(valvePercent, 0, 100, 0, 180);
  valveServo.write(servoAngle);

  // 3. Điều khiển LED & Còi Buzzer đa cấp độ
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
      // Mức dâng cảnh báo: LED Vàng sáng, Còi báo nhẹ ngắt quãng thưa (chu kỳ 1500ms, bíp 120ms)
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
      // Ngập nghiêm trọng: LED Đỏ chớp nháy dồn dập (chu kỳ 250ms), Còi hú liên tục không ngắt
      digitalWrite(PIN_LED_GREEN, LOW);
      digitalWrite(PIN_LED_YELLOW, LOW);
      digitalWrite(PIN_LED_RED, (now % 250 < 125) ? HIGH : LOW);
      tone(PIN_BUZZER, 2500);
      break;
  }
}


// ==========================================
// WEB SERVER TELEMETRY & DASHBOARD (UC07, UC08)
// ==========================================
const char HTML_DASHBOARD[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FloodGuard - He Thong Chong Ngap Thong Minh</title>
  <style>
    :root {
      --bg: #0b132b;
      --card-bg: rgba(28, 37, 65, 0.75);
      --border: rgba(255, 255, 255, 0.12);
      --accent: #00f2fe;
      --text: #e0e6ed;
      --normal: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --critical: #dc2626;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background: radial-gradient(circle at top, #1c2541, var(--bg)); color: var(--text); min-height: 100vh; padding: 20px; }
    .header { text-align: center; margin-bottom: 25px; }
    .header h1 { font-size: 26px; color: #4facfe; text-transform: uppercase; letter-spacing: 1.5px; }
    .header p { color: #8d99ae; font-size: 14px; margin-top: 5px; }
    .container { max-width: 900px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; }
    .card { background: var(--card-bg); backdrop-filter: blur(10px); border: 1px solid var(--border); border-radius: 14px; padding: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.3); }
    .card h2 { font-size: 15px; text-transform: uppercase; color: #a0aec0; margin-bottom: 15px; letter-spacing: 1px; display: flex; align-items: center; justify-content: space-between; }
    .metric-val { font-size: 38px; font-weight: 700; color: #fff; margin-bottom: 8px; }
    .progress-bar { background: rgba(255,255,255,0.08); border-radius: 10px; height: 16px; overflow: hidden; position: relative; margin-top: 10px; }
    .progress-fill { height: 100%; width: 0%; transition: width 0.4s ease, background-color 0.4s ease; border-radius: 10px; }
    .status-badge { display: inline-block; padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; }
    .badge-normal { background: rgba(16, 185, 129, 0.2); color: var(--normal); border: 1px solid var(--normal); }
    .badge-warning { background: rgba(245, 158, 11, 0.2); color: var(--warning); border: 1px solid var(--warning); }
    .badge-danger { background: rgba(239, 68, 68, 0.2); color: var(--danger); border: 1px solid var(--danger); }
    .badge-critical { background: rgba(220, 38, 38, 0.35); color: #ff6b6b; border: 1px solid var(--critical); animation: pulse 1s infinite alternate; }
    @keyframes pulse { from { opacity: 0.7; } to { opacity: 1; } }
    .control-btn { background: #3a86ff; color: white; border: none; padding: 10px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: 0.2s; margin-right: 8px; margin-top: 8px; }
    .control-btn:hover { background: #2563eb; transform: translateY(-1px); }
    .control-btn.active { background: #10b981; }
    .control-btn.danger { background: #ef4444; }
    .info-row { display: flex; justify-content: space-between; margin-top: 12px; font-size: 14px; color: #cbd5e1; border-bottom: 1px dashed rgba(255,255,255,0.08); padding-bottom: 6px; }
    .manual-panel { grid-column: 1 / -1; }
  </style>
</head>
<body>
  <div class="header">
    <h1>FloodGuard System</h1>
    <p>Giam Sat & Dieu Khien Chong Ngap Thoi Gian Thuc</p>
  </div>

  <div class="container">
    <div class="card">
      <h2>Muc Nuoc Ho Thu <span id="distVal">-- cm</span> <small style="font-size:12px;color:#94a3b8;font-weight:normal;">(50cm - 5cm)</small></h2>
      <div class="metric-val" id="waterVal">0%</div>
      <div class="progress-bar">
        <div class="progress-fill" id="waterBar"></div>
      </div>
      <div class="info-row">
        <span>Trang thai canh bao:</span>
        <span id="stateBadge" class="status-badge badge-normal">NORMAL</span>
      </div>
    </div>

    <div class="card">
      <h2>Thoi Tiet & Cam Bien</h2>
      <div class="info-row">
        <span>Cam bien mua:</span>
        <strong id="rainVal">KHONG MUA</strong>
      </div>
      <div class="info-row">
        <span>Do am / ADC mua:</span>
        <span id="rainAdcVal">--</span>
      </div>
      <div class="info-row">
        <span>Che do van hanh:</span>
        <span id="modeBadge" class="status-badge badge-normal">AUTO</span>
      </div>
    </div>

    <div class="card">
      <h2>Thiet Bi Chap Hanh</h2>
      <div class="info-row">
        <span>May bom thoat nuoc:</span>
        <strong id="pumpVal">OFF</strong>
      </div>
      <div class="info-row">
        <span>Van xa servo:</span>
        <strong id="valveVal">0% (Dong)</strong>
      </div>
      <div class="info-row">
        <span>Coi bao dong:</span>
        <span id="buzzerVal">TAT</span>
      </div>
    </div>

    <div class="card manual-panel">
      <h2>Bang Dieu Khien Tu Xa</h2>
      <div>
        <button class="control-btn" onclick="sendCommand('mode_toggle')">Doi Che Do (AUTO / MANUAL)</button>
        <span id="manNotice" style="color: #94a3b8; font-size: 13px; margin-left: 10px;">Chuyen sang MANUAL de can thiep thiet bi:</span>
      </div>
      <div style="margin-top: 12px;">
        <button class="control-btn" id="btnWebPump" onclick="sendCommand('pump_toggle')">Bat/Tat Bom (Manual)</button>
        <button class="control-btn" onclick="sendCommand('valve_0')">Van 0% (Dong)</button>
        <button class="control-btn" onclick="sendCommand('valve_50')">Van 50% (Mo Nua)</button>
        <button class="control-btn" onclick="sendCommand('valve_100')">Van 100% (Mo Het)</button>
      </div>
    </div>
  </div>

  <script>
    async function updateStatus() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();
        
        document.getElementById('waterVal').innerText = data.water + '%';
        document.getElementById('distVal').innerText = data.distance.toFixed(1) + ' cm';
        
        const bar = document.getElementById('waterBar');
        bar.style.width = data.water + '%';
        if (data.water < 21) bar.style.backgroundColor = 'var(--normal)';
        else if (data.water < 41) bar.style.backgroundColor = 'var(--warning)';
        else if (data.water < 71) bar.style.backgroundColor = 'var(--danger)';
        else bar.style.backgroundColor = 'var(--critical)';

        const badge = document.getElementById('stateBadge');
        badge.innerText = data.state;
        badge.className = 'status-badge ' + (
          data.state === 'NORMAL' ? 'badge-normal' :
          data.state === 'WARNING' ? 'badge-warning' :
          data.state === 'DANGER' ? 'badge-danger' : 'badge-critical'
        );

        document.getElementById('rainVal').innerText = data.rain ? 'CO MUA !' : 'KHONG MUA';
        document.getElementById('rainVal').style.color = data.rain ? '#38bdf8' : '#cbd5e1';
        document.getElementById('rainAdcVal').innerText = data.rain_adc;

        const mBadge = document.getElementById('modeBadge');
        mBadge.innerText = data.mode;
        mBadge.className = 'status-badge ' + (data.mode === 'AUTO' ? 'badge-normal' : 'badge-warning');

        const pVal = document.getElementById('pumpVal');
        pVal.innerText = data.pump ? 'DANG BAT (ON)' : 'DA TAT (OFF)';
        pVal.style.color = data.pump ? '#10b981' : '#f87171';

        document.getElementById('valveVal').innerText = data.valve + '%';
        const bVal = document.getElementById('buzzerVal');
        if (data.state === 'CRITICAL' || data.buzzer === 'CONTINUOUS' || data.buzzer === 'true') {
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
        console.error(err);
      }
    }

    async function sendCommand(cmd) {
      await fetch('/api/control?action=' + cmd);
      updateStatus();
    }

    setInterval(updateStatus, 1000);
    updateStatus();
  </script>
</body>
</html>
)rawliteral";

void handleRoot() {
  server.send(200, "text/html", HTML_DASHBOARD);
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
  if (server.hasArg("action")) {
    String act = server.arg("action");
    if (act == "mode_toggle") {
      isAutoMode = !isAutoMode;
    } else if (act == "pump_toggle" && !isAutoMode) {
      pumpState = !pumpState;
    } else if (act == "valve_0" && !isAutoMode) {
      valvePercent = 0;
    } else if (act == "valve_50" && !isAutoMode) {
      valvePercent = 50;
    } else if (act == "valve_100" && !isAutoMode) {
      valvePercent = 100;
    }
  }
  server.send(200, "text/plain", "OK");
}

// ==========================================
// SETUP & LOOP
// ==========================================
void setup() {
  Serial.begin(115200);
  Serial.println("\n--- FLOODGUARD KHOI DONG ---");

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

  // Khởi tạo Servo
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
}

void loop() {
  // 1. Phục vụ yêu cầu Web Server
  server.handleClient();

  // 2. Chu kỳ đọc cảm biến và đánh giá logic (mỗi 100ms)
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
