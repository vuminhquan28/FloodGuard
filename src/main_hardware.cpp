#include <Arduino.h>
#include <ESP32Servo.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>

// ==========================================
// CẤU HÌNH PHẦN CỨNG THẬT (ESP32 HARDWARE)
// Chế độ: SoftAP (ESP32 tự phát Wi-Fi)
// ==========================================
#define PIN_TRIG        18
#define PIN_ECHO        5
#define PIN_RAIN_ADC    34   // Cảm biến mưa (Chân Analog AO)
#define PIN_SERVO       13   // Điều khiển van xả nước SG90
#define PIN_RELAY       23   // Điều khiển Relay máy bơm 5V
#define PIN_BUZZER      19   // Còi báo động Active Buzzer
#define PIN_LED_GREEN   25   // LED trạng thái NORMAL
#define PIN_LED_YELLOW  26   // LED trạng thái WARNING
#define PIN_LED_RED     27   // LED trạng thái DANGER / CRITICAL

// Thông tin mạng Wi-Fi do ESP32 tự phát (SoftAP)
const char* AP_SSID = "FloodGuard_AP";
const char* AP_PASS = "12345678"; // Tối thiểu 8 ký tự (hoặc để "" nếu không cần pass)

// ==========================================
// THÔNG SỐ ĐO VÀ NGƯỠNG MỰC NƯỚC
// ==========================================
const float DISTANCE_EMPTY = 200.0; // Khoảng cách cạn hồ (cm) - 0%
const float DISTANCE_FULL  = 20.0;  // Khoảng cách đầy tràn (cm) - 100%

// Dải trễ (Hysteresis)
const int THRESHOLD_WARN_ENTER   = 21;
const int THRESHOLD_DANGER_ENTER = 41;
const int THRESHOLD_CRIT_ENTER   = 71;

const int THRESHOLD_DANGER_EXIT  = 40;
const int THRESHOLD_WARN_EXIT    = 20;

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
float currentDistance = 200.0;
bool isRaining        = false;
int rainRawADC        = 0;

bool pumpState        = false;
int valvePercent      = 0; // 0%, 50%, 100%
bool isAutoMode       = true;

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

  long duration = pulseIn(PIN_ECHO, HIGH, 30000); // Timeout 30ms (~5m)
  if (duration <= 0) return currentDistance;

  float dist = (duration * 0.0343) / 2.0;
  return dist;
}

void updateSensors() {
  float d = readUltrasonicCM();
  if (d < DISTANCE_FULL)  d = DISTANCE_FULL;
  if (d > DISTANCE_EMPTY) d = DISTANCE_EMPTY;
  currentDistance = d;

  // Tính phần trăm mực nước
  float pct = ((DISTANCE_EMPTY - currentDistance) / (DISTANCE_EMPTY - DISTANCE_FULL)) * 100.0;
  waterPercent = (int)constrain(pct, 0.0, 100.0);

  // Đọc cảm biến mưa (ESP32 ADC 12-bit: 0 - 4095)
  // Khi có nước mưa tiếp xúc -> Điện trở giảm -> Giá trị ADC giảm (< 2500)
  rainRawADC = analogRead(PIN_RAIN_ADC);
  isRaining = (rainRawADC < 2500);
}

// ==========================================
// THUẬT TOÁN FSM VÀ HYSTERESIS
// ==========================================
void evaluateSystemStateAuto() {
  if (!isAutoMode) return;

  switch (sysState) {
    case STATE_NORMAL:
      if (waterPercent >= THRESHOLD_WARN_ENTER) {
        sysState = STATE_WARNING;
      }
      break;

    case STATE_WARNING:
      if (waterPercent >= THRESHOLD_DANGER_ENTER) {
        sysState = STATE_DANGER;
      } else if (waterPercent < THRESHOLD_WARN_EXIT) {
        sysState = STATE_NORMAL;
      }
      break;

    case STATE_DANGER:
      if (waterPercent >= THRESHOLD_CRIT_ENTER) {
        sysState = STATE_CRITICAL;
      } else if (waterPercent < THRESHOLD_DANGER_EXIT) {
        sysState = STATE_WARNING;
      }
      break;

    case STATE_CRITICAL:
      if (waterPercent < THRESHOLD_CRIT_ENTER) {
        sysState = STATE_DANGER;
      }
      break;
  }

  // Gán đầu ra theo trạng thái AUTO
  switch (sysState) {
    case STATE_NORMAL:
      pumpState    = false;
      valvePercent = 0;
      break;
    case STATE_WARNING:
      pumpState    = false;
      valvePercent = 0;
      break;
    case STATE_DANGER:
      pumpState    = true;
      valvePercent = 50;
      break;
    case STATE_CRITICAL:
      pumpState    = true;
      valvePercent = 100;
      break;
  }
}

// ==========================================
// ÁP ĐẶT ĐẦU RA (ACTUATORS & LEDS)
// ==========================================
void applyOutputs() {
  // 1. Máy bơm (Relay kích HIGH/LOW tùy module, ở đây HIGH là BẬT)
  digitalWrite(PIN_RELAY, pumpState ? HIGH : LOW);

  // 2. Góc mở Servo (0% = 0 độ, 50% = 90 độ, 100% = 180 độ)
  int angle = map(valvePercent, 0, 100, 0, 180);
  valveServo.write(angle);

  // 3. Đèn LED chỉ thị
  switch (sysState) {
    case STATE_NORMAL:
      digitalWrite(PIN_LED_GREEN, HIGH);
      digitalWrite(PIN_LED_YELLOW, LOW);
      digitalWrite(PIN_LED_RED, LOW);
      noTone(PIN_BUZZER);
      break;

    case STATE_WARNING:
      digitalWrite(PIN_LED_GREEN, LOW);
      digitalWrite(PIN_LED_YELLOW, HIGH);
      digitalWrite(PIN_LED_RED, LOW);
      noTone(PIN_BUZZER);
      break;

    case STATE_DANGER:
      digitalWrite(PIN_LED_GREEN, LOW);
      digitalWrite(PIN_LED_YELLOW, LOW);
      digitalWrite(PIN_LED_RED, HIGH);
      noTone(PIN_BUZZER);
      break;

    case STATE_CRITICAL:
      digitalWrite(PIN_LED_GREEN, LOW);
      digitalWrite(PIN_LED_YELLOW, LOW);
      // Chớp nháy LED đỏ và còi hú khẩn cấp (non-blocking)
      unsigned long now = millis();
      if (now - lastBuzzerBlink >= 200) {
        lastBuzzerBlink = now;
        buzzerToggle = !buzzerToggle;
        digitalWrite(PIN_LED_RED, buzzerToggle ? HIGH : LOW);
        if (buzzerToggle) {
          tone(PIN_BUZZER, 2000);
        } else {
          noTone(PIN_BUZZER);
        }
      }
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
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>FLOODGUARD DASHBOARD</h1>
      <p>Hệ Thống Chống Ngập Thông Minh (ESP32 Hardware AP Mode)</p>
      <div class="network-badge">📶 Wi-Fi: FloodGuard_AP | IP: 192.168.4.1</div>
    </header>

    <div class="grid">
      <!-- Mực nước -->
      <div class="card">
        <div class="card-title">Mực Nước Hồ Thu</div>
        <div class="card-value" id="waterVal">0%</div>
        <div style="font-size: 0.85rem; color: var(--text-muted);">Khoảng cách: <span id="distVal">--</span> cm</div>
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
      <div class="card-title">Bảng Điều Khiển Can Thiệp Thủ Công (Manual Override)</div>
      <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 12px;">
        Chuyển sang chế độ MANUAL để tự do bật/tắt bơm và xoay góc mở van xả.
      </p>
      <div>
        <button class="control-btn control-btn-primary" onclick="sendCommand('mode_toggle')">Đổi Chế Độ (AUTO / MANUAL)</button>
        <button class="control-btn" id="btnWebPump" onclick="sendCommand('pump_toggle')">Bật/Tắt Bơm (Manual)</button>
        <button class="control-btn" onclick="sendCommand('valve_0')">Van 0% (Đóng)</button>
        <button class="control-btn" onclick="sendCommand('valve_50')">Van 50% (Mở Nửa)</button>
        <button class="control-btn control-btn-danger" onclick="sendCommand('valve_100')">Van 100% (Mở Hết)</button>
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
        
        const bar = document.getElementById('waterBar');
        bar.style.width = data.water + '%';
        bar.style.background = data.water < 21 ? 'var(--green)' :
                               data.water < 41 ? 'var(--yellow)' : 'var(--red)';

        const sBadge = document.getElementById('stateBadge');
        sBadge.innerText = data.state;
        sBadge.className = 'status-badge ' + (
          data.state === 'NORMAL'   ? 'badge-normal'  :
          data.state === 'WARNING'  ? 'badge-warning' :
          data.state === 'DANGER'   ? 'badge-danger'  : 'badge-critical'
        );

        document.getElementById('rainVal').innerText = data.rain ? 'CÓ MƯA !' : 'KHÔNG MƯA';
        document.getElementById('rainVal').style.color = data.rain ? '#38bdf8' : '#94a3b8';
        document.getElementById('rainAdcVal').innerText = data.rain_adc;

        const mBadge = document.getElementById('modeBadge');
        mBadge.innerText = data.mode;
        mBadge.className = 'status-badge ' + (data.mode === 'AUTO' ? 'badge-normal' : 'badge-warning');

        const pVal = document.getElementById('pumpVal');
        pVal.innerText = data.pump ? 'ĐANG BẬT (ON)' : 'ĐÃ TẮT (OFF)';
        pVal.style.color = data.pump ? '#10b981' : '#f87171';

        document.getElementById('valveVal').innerText = data.valve + '%';
        document.getElementById('buzzerVal').innerText = data.buzzer ? 'ĐANG CÒI HÚ' : 'YÊN LẶNG';
      } catch (err) {
        console.error('Loi cap nhat status:', err);
      }
    }

    async function sendCommand(cmd) {
      try {
        await fetch('/api/control?action=' + cmd);
        updateStatus();
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
  server.send(200, "text/html", HTML_DASHBOARD);
}

void handleStatusApi() {
  const char* stStr = "NORMAL";
  if (sysState == STATE_WARNING)  stStr = "WARNING";
  if (sysState == STATE_DANGER)   stStr = "DANGER";
  if (sysState == STATE_CRITICAL) stStr = "CRITICAL";

  char json[256];
  snprintf(json, sizeof(json),
    "{\"water\":%d,\"distance\":%.1f,\"rain\":%s,\"rain_adc\":%d,\"state\":\"%s\",\"mode\":\"%s\",\"pump\":%s,\"valve\":%d,\"buzzer\":%s}",
    waterPercent,
    currentDistance,
    isRaining ? "true" : "false",
    rainRawADC,
    stStr,
    isAutoMode ? "AUTO" : "MANUAL",
    pumpState ? "true" : "false",
    valvePercent,
    (sysState == STATE_CRITICAL) ? "true" : "false"
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
    applyOutputs();
  }
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

  // Khởi tạo GPIO
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_RAIN_ADC, INPUT);

  pinMode(PIN_RELAY, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_YELLOW, OUTPUT);
  pinMode(PIN_LED_RED, OUTPUT);

  digitalWrite(PIN_RELAY, LOW);
  digitalWrite(PIN_LED_GREEN, LOW);
  digitalWrite(PIN_LED_YELLOW, LOW);
  digitalWrite(PIN_LED_RED, LOW);
  noTone(PIN_BUZZER);

  // Khởi tạo Servo van xả
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
  // 1. Phục vụ yêu cầu Web Server
  server.handleClient();

  // 2. Chu kỳ đọc cảm biến và đánh giá logic (mỗi 100ms)
  unsigned long now = millis();
  if (now - lastSensorRead >= 100) {
    lastSensorRead = now;
    updateSensors();
    evaluateSystemStateAuto();
    applyOutputs();
  }

  delay(10);
}

