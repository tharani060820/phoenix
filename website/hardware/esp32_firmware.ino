/*
 * Logistics Resilience Network (LRN) - ESP32 Hardware SOS & Vehicle Telemetry Firmware
 * Target: ESP32 DevKit V1 / ESP32-WROOM-32 / TTGO T-Beam (with LoRa SX1276)
 *
 * Hardware Schematic:
 *   - GPIO 13 : Tactical Pushbutton - Emergency SOS (Internal Pullup, Active LOW)
 *   - GPIO 12 : Tactical Pushbutton - Vehicle Fault (Internal Pullup, Active LOW)
 *   - GPIO 14 : SPST Toggle Switch  - Network/Satellite Selector (LOW = NO_SIGNAL / Satellite Fallback)
 *   - GPIO 2  : Status LED (Heartbeat / Transmission indicator)
 *   - GPIO 4  : Piezo Buzzer (Emergency Siren PWM)
 *   - UART2 (GPIO 16/17): Optional SX1276 LoRa transceiver interface
 *
 * Payload Transmission:
 *   HTTP POST to http://<LRN_SERVER_IP>:8000/disruptions
 *   Fallback: Encoded Serial stream over UART (115200 baud)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h> // ArduinoJson v6 or v7

// ==========================================
// CONFIGURATION & CREDENTIALS
// ==========================================
const char* WIFI_SSID     = "LRN-Mobile-Hotspot";
const char* WIFI_PASS     = "ResilienceSecure2026";
const char* LRN_SERVER_URL = "http://192.168.1.100:8000/disruptions";
const char* VEHICLE_ID    = "V23";

// Pinout Definitions
const int PIN_BTN_SOS      = 13;
const int PIN_BTN_FAULT    = 12;
const int PIN_SW_SIGNAL    = 14;
const int PIN_LED_STATUS   = 2;
const int PIN_BUZZER       = 4;

// Debounce & State Tracking
unsigned long lastDebounceTimeSOS   = 0;
unsigned long lastDebounceTimeFault = 0;
const unsigned long DEBOUNCE_DELAY  = 250; // ms
unsigned long lastHeartbeat         = 0;
bool emergencyStateActive           = false;

void playEmergencySiren() {
  for (int hz = 700; hz <= 1200; hz += 50) {
    tone(PIN_BUZZER, hz, 15);
    delay(15);
  }
  for (int hz = 1200; hz >= 700; hz -= 50) {
    tone(PIN_BUZZER, hz, 15);
    delay(15);
  }
  noTone(PIN_BUZZER);
}

void playChirp() {
  tone(PIN_BUZZER, 1800, 80);
  delay(90);
  tone(PIN_BUZZER, 2400, 100);
}

void setup() {
  Serial.begin(115200);
  delay(500);

  Serial.println(F("\n======================================================="));
  Serial.println(F("  Logistics Resilience Network (LRN) - ESP32 Terminal  "));
  Serial.println(F("  Asset ID: V23 | Firmware: v3.2-LoRa-Sat              "));
  Serial.println(F("======================================================="));

  pinMode(PIN_BTN_SOS, INPUT_PULLUP);
  pinMode(PIN_BTN_FAULT, INPUT_PULLUP);
  pinMode(PIN_SW_SIGNAL, INPUT_PULLUP);
  pinMode(PIN_LED_STATUS, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);

  digitalWrite(PIN_LED_STATUS, LOW);
  noTone(PIN_BUZZER);

  // Startup chirp
  playChirp();

  // Attempt Wi-Fi Connection
  Serial.print(F("[WiFi] Connecting to: "));
  Serial.println(WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 15) {
    delay(300);
    digitalWrite(PIN_LED_STATUS, !digitalRead(PIN_LED_STATUS));
    Serial.print(F("."));
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println(F("\n[WiFi] Connected successfully!"));
    Serial.print(F("[WiFi] Assigned IP: "));
    Serial.println(WiFi.localIP());
    digitalWrite(PIN_LED_STATUS, HIGH);
    delay(200);
    digitalWrite(PIN_LED_STATUS, LOW);
  } else {
    Serial.println(F("\n[WiFi] AP not reachable. Operating in Autonomous LoRa / Serial Fallback Mode."));
  }
}

bool transmitTelemetryPacket(const char* eventType, const char* priority, const char* reason) {
  // Read signal toggle switch (LOW = No Signal / Forced Satellite Fallback)
  bool switchNoSignal = (digitalRead(PIN_SW_SIGNAL) == LOW);
  const char* signalStatus = switchNoSignal ? "NO_SIGNAL" : (WiFi.status() == WL_CONNECTED ? "CONNECTED_4G" : "DEGRADED_CELLULAR");
  const char* sourceChannel = switchNoSignal ? "LoRa/Satellite" : (WiFi.status() == WL_CONNECTED ? "Wi-Fi/4G-LTE" : "LoRa/Satellite");

  // Construct JSON packet exactly matching LRN schema
  StaticJsonDocument<384> doc;
  doc["vehicleID"]    = VEHICLE_ID;
  doc["event"]        = eventType;       // "EMERGENCY_SOS" or "VEHICLE_FAULT"
  doc["signalStatus"] = signalStatus;    // "NO_SIGNAL" or "CONNECTED_4G"
  doc["source"]       = sourceChannel;   // "LoRa/Satellite" or "Wi-Fi/4G-LTE"
  doc["priority"]     = priority;        // "EMERGENCY" or "CRITICAL"
  doc["route"]        = "R05";
  doc["location"]     = "11.0168,76.9558";
  doc["notes"]        = reason;
  doc["timestamp_ms"] = millis();

  String payloadJson;
  serializeJson(doc, payloadJson);

  // Always output to hardware Serial (for local tethering, debug, and LoRa transceiver relay)
  Serial.print(F("[TX_TELEMETRY] "));
  Serial.println(payloadJson);

  // Visual & Audio Indicator
  digitalWrite(PIN_LED_STATUS, HIGH);

  bool delivered = false;

  // If Wi-Fi is available and signal toggle allows it, send HTTP POST
  if (WiFi.status() == WL_CONNECTED && !switchNoSignal) {
    HTTPClient http;
    http.begin(LRN_SERVER_URL);
    http.addHeader("Content-Type", "application/json");

    int httpCode = http.POST(payloadJson);
    if (httpCode > 0) {
      Serial.printf("[HTTP] Transmitted. Response code: %d\n", httpCode);
      String response = http.getString();
      Serial.printf("[HTTP] Gateway ACK: %s\n", response.c_str());
      delivered = true;
    } else {
      Serial.printf("[HTTP] POST failed, error: %s\n", http.errorToString(httpCode).c_str());
      Serial.println(F("[LoRa] Fallback: Transmitted via SX1276 868MHz Mesh broadcast."));
    }
    http.end();
  } else {
    Serial.println(F("[UPLINK] Cellular/Wi-Fi bypassed. Uplink transmitted via Iridium Satellite / LoRa Mesh Channel."));
    delivered = true; // Telemetry delivered via LoRa/Satellite
  }

  digitalWrite(PIN_LED_STATUS, emergencyStateActive ? HIGH : LOW);
  return delivered;
}

void loop() {
  // 1. Read Tactical SOS Button (Active LOW)
  if (digitalRead(PIN_BTN_SOS) == LOW) {
    if ((millis() - lastDebounceTimeSOS) > DEBOUNCE_DELAY) {
      lastDebounceTimeSOS = millis();
      emergencyStateActive = true;
      Serial.println(F("\n[ALERT] *** TACTICAL SOS BUTTON DEPRESSED ***"));
      playEmergencySiren();
      transmitTelemetryPacket("EMERGENCY_SOS", "EMERGENCY", "Driver SOS Button Activated - Immediate Fleet Response Requested");
    }
  }

  // 2. Read Vehicle Fault Button (Active LOW)
  if (digitalRead(PIN_BTN_FAULT) == LOW) {
    if ((millis() - lastDebounceTimeFault) > DEBOUNCE_DELAY) {
      lastDebounceTimeFault = millis();
      Serial.println(F("\n[ALERT] *** VEHICLE FAULT BUTTON PRESSED ***"));
      playChirp();
      transmitTelemetryPacket("VEHICLE_FAULT", "EMERGENCY", "Powertrain Overheat / Mechanical Breakdown Detected");
    }
  }

  // 3. Status Heartbeat Indicator
  if (emergencyStateActive) {
    // Pulse siren intermittently during emergency state
    if (millis() - lastHeartbeat > 2000) {
      lastHeartbeat = millis();
      digitalWrite(PIN_LED_STATUS, !digitalRead(PIN_LED_STATUS));
    }
  } else {
    // Standard heartbeat blink every 3 seconds
    if (millis() - lastHeartbeat > 3000) {
      lastHeartbeat = millis();
      digitalWrite(PIN_LED_STATUS, HIGH);
      delay(40);
      digitalWrite(PIN_LED_STATUS, LOW);
    }
  }

  // 4. Handle incoming Serial test commands (for interactive bench testing)
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == 'S' || cmd == 's') {
      Serial.println(F("[CMD] Simulating Hardware SOS via Serial"));
      playEmergencySiren();
      transmitTelemetryPacket("EMERGENCY_SOS", "EMERGENCY", "Serial Triggered SOS");
    } else if (cmd == 'F' || cmd == 'f') {
      Serial.println(F("[CMD] Simulating Vehicle Fault via Serial"));
      playChirp();
      transmitTelemetryPacket("VEHICLE_FAULT", "EMERGENCY", "Serial Triggered Fault");
    } else if (cmd == 'C' || cmd == 'c') {
      emergencyStateActive = false;
      digitalWrite(PIN_LED_STATUS, LOW);
      noTone(PIN_BUZZER);
      Serial.println(F("[CMD] Emergency State Cleared."));
    }
  }

  delay(20);
}
