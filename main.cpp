#include <Arduino.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Định nghĩa chân cắm ESP32 theo diagram.json
#define TRIG_PIN       18
#define ECHO_PIN       5
#define RAIN_PIN       34    // Chiết áp mô phỏng cảm biến mưa (ADC)
#define FLOW_PIN       4     // Máy phát xung mô phỏng cảm biến lưu lượng
#define RELAY_PIN      23    // Điều khiển Relay máy bơm
#define BUZZER_PIN     19    // Loa còi báo động
#define LED_RED_PIN    2     // Đèn đỏ: Báo nguy hiểm / Kẹt bơm
#define LED_YEL_PIN    15    // Đèn vàng: Báo mưa to / Cảnh báo sớm

// Ngưỡng hoạt động (cm)
const float THRESHOLD_DANGER = 100.0; // Khoảng cách < 100cm: Nguy cơ ngập cao
const float THRESHOLD_EARLY  = 130.0; // Khoảng cách < 130cm kết hợp mưa: Kích hoạt sớm
const float THRESHOLD_SAFE   = 160.0; // Khoảng cách > 160cm: Nước rút an toàn
const int   RAIN_HEAVY_ADC   = 2000;  // Ngưỡng ADC nhận diện mưa lớn

volatile unsigned long pulseCount = 0;
unsigned long prevTime = 0;
float flowRate = 0.0;
bool isPumpActive = false;

LiquidCrystal_I2C lcd(0x27, 16, 2);

// ISR: Đếm xung cảm biến dòng chảy
void IRAM_ATTR pulseCounter() {
  pulseCount++;
}

float measureDistanceCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  if (duration == 0) return 400.0;
  return duration * 0.0343 / 2.0;
}

void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(LED_YEL_PIN, OUTPUT);
  pinMode(FLOW_PIN, INPUT_PULLUP);

  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(LED_RED_PIN, LOW);
  digitalWrite(LED_YEL_PIN, LOW);
  noTone(BUZZER_PIN);

  attachInterrupt(digitalPinToInterrupt(FLOW_PIN), pulseCounter, RISING);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("HE THONG CHONG");
  lcd.setCursor(0, 1);
  lcd.print("NGAP THONG MINH");
  delay(1500);
  lcd.clear();
}

void loop() {
  unsigned long currentTime = millis();

  float distance = measureDistanceCM();
  int rainADC = analogRead(RAIN_PIN);
  bool isRaining = (rainADC > RAIN_HEAVY_ADC);

  // Đèn vàng báo mưa
  digitalWrite(LED_YEL_PIN, isRaining ? HIGH : LOW);

  // Cập nhật tính toán lưu lượng và xử lý logic mỗi 1 giây
  if (currentTime - prevTime >= 1000) {
    noInterrupts();
    unsigned long currentPulses = pulseCount;
    pulseCount = 0;
    interrupts();

    // Hệ số YF-S201: F = 7.5 * Q (L/min)
    flowRate = ((float)currentPulses / 7.5);
    prevTime = currentTime;

    // 1. Kích hoạt máy bơm
    if (distance < THRESHOLD_DANGER || (isRaining && distance < THRESHOLD_EARLY)) {
      isPumpActive = true;
      digitalWrite(RELAY_PIN, HIGH);
    } 
    // 2. Ngắt máy bơm khi an toàn
    else if (distance > THRESHOLD_SAFE) {
      isPumpActive = false;
      digitalWrite(RELAY_PIN, LOW);
      digitalWrite(LED_RED_PIN, LOW);
      noTone(BUZZER_PIN);
    }

    // 3. Logic cảnh báo còi & LED đỏ kẹt bơm
    if (isPumpActive) {
      if (flowRate < 0.5) {
        // Sự cố: Bơm mở nhưng không có dòng chảy
        digitalWrite(LED_RED_PIN, HIGH);
        tone(BUZZER_PIN, 1800);
        lcd.setCursor(0, 1);
        lcd.print("ERR: KET BOM!   ");
      } else {
        // Đang bơm bình thường
        digitalWrite(LED_RED_PIN, LOW);
        tone(BUZZER_PIN, 600);
        lcd.setCursor(0, 1);
        lcd.printf("F:%.1fL/m BOM CHAY", flowRate);
      }
    } else {
      noTone(BUZZER_PIN);
      lcd.setCursor(0, 1);
      lcd.printf("F:%.1fL/m AN TOAN ", flowRate);
    }

    // Dòng 1 LCD: Khoảng cách & Mưa
    lcd.setCursor(0, 0);
    lcd.printf("D:%.0fcm MUA:%s", distance, isRaining ? "CO " : "KHO");

    Serial.printf("Dist: %.1fcm | Rain: %d | Flow: %.1f L/m | Pump: %s\n",
                  distance, rainADC, flowRate, isPumpActive ? "ON" : "OFF");
  }

  delay(100);
}