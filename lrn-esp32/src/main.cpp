#include <Arduino.h>

// ============================================================
// LOGI-PULSE
// Smart Truck Breakdown Detection + SOS Verification
// ESP32 + Wokwi + VS Code
// ============================================================

// ---------------- PIN CONFIGURATION ----------------
const int BTN_START = 25;       // Start route
const int BTN_STOP  = 26;       // Normal stop
const int BTN_SOS   = 27;       // Driver SOS

const int SW_ENGINE    = 13;    // Engine fault
const int SW_BATTERY   = 14;    // Battery fault
const int SW_TEMP      = 16;    // High temperature
const int SW_VIBRATION = 17;    // Abnormal vibration
const int SW_NOSIGNAL  = 18;    // No signal simulation

const int LED_GREEN  = 2;       // Normal
const int LED_YELLOW = 15;      // Verify
const int LED_RED    = 19;      // Breakdown
const int BUZZER     = 21;

// ---------------- VEHICLE CONFIG ----------------
const char* VEHICLE_ID = "V23";

const float VIRTUAL_SPEED_KMH = 60.0;

// Wokwi demo:
// 0.50 virtual km per real second
// 10 seconds = 5 km
const float DEMO_KM_PER_SECOND = 0.50;

const float MIN_MOVEMENT_KM = 3.0;

// ---------------- STATE ----------------
bool routeActive = false;
bool truckStopped = true;
bool breakdownConfirmed = false;
bool claimReceived = false;

float distanceKm = 0.0;
float currentSpeedKmh = 0.0;

unsigned long lastDistanceUpdate = 0;
unsigned long lastPrint = 0;

// Button states
bool lastStartState = HIGH;
bool lastStopState = HIGH;
bool lastSOSState = HIGH;

// ============================================================
// LED FUNCTIONS
// ============================================================

void setReadyLEDs() {
  digitalWrite(LED_GREEN, HIGH);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);
}

void setVerificationLEDs() {
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, HIGH);
  digitalWrite(LED_RED, LOW);
}

void setBreakdownLEDs() {
  digitalWrite(LED_GREEN, LOW);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, HIGH);
}

// ============================================================
// BUZZER
// ============================================================

void beep(int ms) {
  digitalWrite(BUZZER, HIGH);
  delay(ms);
  digitalWrite(BUZZER, LOW);
}

// ============================================================
// BUTTON DEBOUNCE
// ============================================================

bool buttonPressed(int pin, bool &lastState) {

  bool currentState = digitalRead(pin);

  bool pressed =
      (lastState == HIGH && currentState == LOW);

  if (pressed) {
    delay(30);
    currentState = digitalRead(pin);
  }

  lastState = currentState;

  return pressed;
}

// ============================================================
// SENSOR INPUTS
// ============================================================

bool engineFault() {
  return digitalRead(SW_ENGINE) == LOW;
}

bool batteryFault() {
  return digitalRead(SW_BATTERY) == LOW;
}

bool temperatureFault() {
  return digitalRead(SW_TEMP) == LOW;
}

bool vibrationFault() {
  return digitalRead(SW_VIBRATION) == LOW;
}

bool physicalFaultPresent() {

  return engineFault() ||
         batteryFault() ||
         temperatureFault() ||
         vibrationFault();
}

const char* transportSource() {

  if (digitalRead(SW_NOSIGNAL) == LOW)
    return "LoRa/Satellite";

  return "WIFI";
}

// ============================================================
// BREAKDOWN CONFIDENCE SCORE
// ============================================================

int calculateConfidenceScore() {

  int score = 0;

  // Truck stopped
  if (truckStopped)
    score += 20;

  // Truck actually travelled before stopping
  if (distanceKm >= MIN_MOVEMENT_KM)
    score += 10;

  // Physical evidence
  if (engineFault())
    score += 30;

  if (batteryFault())
    score += 15;

  if (temperatureFault())
    score += 15;

  if (vibrationFault())
    score += 10;

  if (score > 100)
    score = 100;

  return score;
}

// ============================================================
// CLASSIFICATION
// ============================================================

const char* classificationFromScore(int score) {

  if (score >= 70)
    return "HIGH CONFIDENCE - BREAKDOWN SUPPORTED";

  if (score >= 40)
    return "NEEDS VERIFICATION";

  return "LOW CONFIDENCE - STOP ONLY / WEAK EVIDENCE";
}

// ============================================================
// PRINT EVIDENCE
// ============================================================

void printEvidence() {

  int score = calculateConfidenceScore();

  Serial.println();
  Serial.println("================================================");
  Serial.println("       PROOF-OF-BREAKDOWN VERIFICATION");
  Serial.println("================================================");

  Serial.printf("Vehicle ID            : %s\n", VEHICLE_ID);

  Serial.printf(
      "Truck stopped         : %s\n",
      truckStopped ? "YES" : "NO"
  );

  Serial.printf(
      "Current speed         : %.1f km/h\n",
      currentSpeedKmh
  );

  Serial.printf(
      "Distance before event : %.2f km\n",
      distanceKm
  );

  Serial.printf(
      "Engine fault          : %s\n",
      engineFault() ? "YES" : "NO"
  );

  Serial.printf(
      "Battery abnormal      : %s\n",
      batteryFault() ? "YES" : "NO"
  );

  Serial.printf(
      "Temperature abnormal  : %s\n",
      temperatureFault() ? "YES" : "NO"
  );

  Serial.printf(
      "Vibration abnormal    : %s\n",
      vibrationFault() ? "YES" : "NO"
  );

  Serial.printf(
      "Confidence score      : %d%%\n",
      score
  );

  Serial.printf(
      "Classification        : %s\n",
      classificationFromScore(score)
  );

  Serial.println("-----------------------------------------------");

  if (score >= 70) {

    Serial.println(
        "DECISION: BREAKDOWN CONFIRMED / RECOVERY MAY START"
    );

  } else if (score >= 40) {

    Serial.println(
        "DECISION: REQUEST INSPECTION / PHOTO / VIDEO"
    );

  } else {

    Serial.println(
        "DECISION: DO NOT REASSIGN YET - REQUEST VERIFICATION"
    );
  }

  Serial.println("================================================");
  Serial.flush();
}

// ============================================================
// SOS PACKET
// ============================================================

void sendSOS(const char* trigger) {

  int score = calculateConfidenceScore();

  const char* classification =
      classificationFromScore(score);

  String json = "{";

  json += "\"vehicle_id\":\"";
  json += VEHICLE_ID;
  json += "\",";

  json += "\"event\":\"BREAKDOWN_SOS\",";

  json += "\"trigger\":\"";
  json += trigger;
  json += "\",";

  json += "\"speed_kmh\":";
  json += String(currentSpeedKmh, 1);
  json += ",";

  json += "\"distance_km\":";
  json += String(distanceKm, 2);
  json += ",";

  json += "\"engine_fault\":";
  json += engineFault() ? "true" : "false";
  json += ",";

  json += "\"battery_fault\":";
  json += batteryFault() ? "true" : "false";
  json += ",";

  json += "\"temperature_fault\":";
  json += temperatureFault() ? "true" : "false";
  json += ",";

  json += "\"vibration_fault\":";
  json += vibrationFault() ? "true" : "false";
  json += ",";

  json += "\"confidence\":";
  json += String(score);
  json += ",";

  json += "\"classification\":\"";
  json += classification;
  json += "\",";

  json += "\"source\":\"";
  json += transportSource();
  json += "\"";

  json += "}";

  Serial.println();
  Serial.println("*************** SOS PACKET ***************");

  Serial.println(json);

  Serial.printf(
      "Transport source : %s\n",
      transportSource()
  );

  Serial.println("******************************************");
  Serial.flush();

  if (score >= 70) {

    setBreakdownLEDs();

    beep(200);
    delay(100);
    beep(200);

  } else if (score >= 40) {

    setVerificationLEDs();

    beep(120);

  } else {

    setVerificationLEDs();

    beep(80);
  }
}

// ============================================================
// START ROUTE
// ============================================================

void startRoute() {

  routeActive = true;

  truckStopped = false;

  breakdownConfirmed = false;

  claimReceived = false;

  distanceKm = 0.0;

  currentSpeedKmh = VIRTUAL_SPEED_KMH;

  lastDistanceUpdate = millis();
  lastPrint = 0;

  Serial.printf(
      "MOVING | Speed: %.1f km/h | Distance: %.2f km\n",
      currentSpeedKmh,
      distanceKm
  );

  setReadyLEDs();

  Serial.println();
  Serial.println("========== ROUTE STARTED ==========");

  Serial.printf(
      "Vehicle ID    : %s\n",
      VEHICLE_ID
  );

  Serial.printf(
      "Virtual speed : %.1f km/h\n",
      currentSpeedKmh
  );

  Serial.println(
      "Truck is moving..."
  );

  Serial.println(
      "==================================="
  );
}

// ============================================================
// NORMAL STOP
// ============================================================

void normalStop() {

  if (!routeActive) {
    Serial.println();
    Serial.println("Truck is already stopped. Evaluating vehicle evidence...");
    printEvidence();
    return;
  }

  routeActive = false;

  truckStopped = true;

  currentSpeedKmh = 0.0;

  Serial.println();
  Serial.println("========== TRUCK STOPPED ==========");

  Serial.printf(
      "Distance travelled : %.2f km\n",
      distanceKm
  );

  Serial.println(
      "STOP alone does NOT prove breakdown."
  );

  if (physicalFaultPresent()) {

    breakdownConfirmed = true;

    Serial.println(
        "Physical fault evidence detected."
    );

    printEvidence();

    sendSOS(
        "AUTOMATIC_BREAKDOWN_DETECTED"
    );

  } else {

    setVerificationLEDs();

    printEvidence();
  }
}

// ============================================================
// DRIVER SOS
// ============================================================

void processDriverSOS() {

  claimReceived = true;

  routeActive = false;

  truckStopped = true;

  currentSpeedKmh = 0.0;

  Serial.println();
  Serial.println("========== DRIVER SOS ==========");

  Serial.println(
      "Driver reported: TRUCK BREAKDOWN"
  );

  Serial.println(
      "SOS claim is NOT proof by itself."
  );

  Serial.println(
      "Checking vehicle evidence..."
  );

  int score =
      calculateConfidenceScore();

  breakdownConfirmed =
      (score >= 70);

  printEvidence();

  sendSOS(
      "DRIVER_SOS_CLAIM"
  );
}

// ============================================================
// AUTOMATIC BREAKDOWN DETECTION
// ============================================================

void monitorForAutomaticBreakdown() {

  if (!routeActive)
    return;

  // In Wokwi, activating any fault switch while
  // the truck is moving simulates a sudden failure.

  if (physicalFaultPresent()) {

    routeActive = false;

    truckStopped = true;

    currentSpeedKmh = 0.0;

    breakdownConfirmed = true;

    Serial.println();
    Serial.println(
        "!!!!!!!! AUTOMATIC BREAKDOWN DETECTED !!!!!!!!"
    );

    Serial.println(
        "Physical fault appeared while vehicle was moving."
    );

    Serial.println(
        "Virtual vehicle stopped automatically."
    );

    printEvidence();

    sendSOS(
        "AUTOMATIC_SENSOR_DETECTION"
    );
  }
}

// ============================================================
// MOVEMENT SIMULATION
// ============================================================

void updateDistance() {

  if (!routeActive)
    return;

  unsigned long now = millis();

  unsigned long elapsedMs =
      now - lastDistanceUpdate;

  lastDistanceUpdate = now;

  float elapsedSeconds =
      elapsedMs / 1000.0;

  distanceKm +=
      elapsedSeconds * DEMO_KM_PER_SECOND;

  if (now - lastPrint >= 1000) {

    lastPrint = now;

    Serial.printf(
        "MOVING | Speed: %.1f km/h | Distance: %.2f km\n",
        currentSpeedKmh,
        distanceKm
    );
  }
}

// ============================================================
// SETUP
// ============================================================

void setup() {

  Serial.begin(115200);

  delay(500);

  // Buttons
  pinMode(
      BTN_START,
      INPUT_PULLUP
  );

  pinMode(
      BTN_STOP,
      INPUT_PULLUP
  );

  pinMode(
      BTN_SOS,
      INPUT_PULLUP
  );

  // Fault switches
  pinMode(
      SW_ENGINE,
      INPUT_PULLUP
  );

  pinMode(
      SW_BATTERY,
      INPUT_PULLUP
  );

  pinMode(
      SW_TEMP,
      INPUT_PULLUP
  );

  pinMode(
      SW_VIBRATION,
      INPUT_PULLUP
  );

  pinMode(
      SW_NOSIGNAL,
      INPUT_PULLUP
  );

  // Outputs
  pinMode(
      LED_GREEN,
      OUTPUT
  );

  pinMode(
      LED_YELLOW,
      OUTPUT
  );

  pinMode(
      LED_RED,
      OUTPUT
  );

  pinMode(
      BUZZER,
      OUTPUT
  );

  digitalWrite(
      BUZZER,
      LOW
  );

  setReadyLEDs();

  Serial.println();
  Serial.println("================================================");
  Serial.println("             LOGI-PULSE TRUCK NODE");
  Serial.println("     SMART BREAKDOWN + SOS VERIFICATION");
  Serial.println("================================================");

  Serial.println("START  = Start virtual truck");

  Serial.println("STOP   = Normal stop");

  Serial.println("SOS    = Driver breakdown claim");

  Serial.println(
      "ENGINE/BATTERY/TEMP/VIBRATION = Vehicle evidence"
  );

  Serial.println(
      "NO SIGNAL = Simulated LoRa/Satellite"
  );

  Serial.println();

  Serial.println(
      "IMPORTANT:"
  );

  Serial.println(
      "Truck STOP alone does not mean breakdown."
  );

  Serial.println(
      "SOS alone does not prove breakdown."
  );

  Serial.println(
      "Independent physical evidence is checked."
  );

  Serial.println(
      "================================================"
  );
  Serial.println("READY. Press START (Green) to begin route,");
  Serial.println("SOS (Red) to report breakdown, or STOP (Blue) to verify.");
  Serial.println("================================================");
  Serial.flush();
}

// ============================================================
// LOOP
// ============================================================

void loop() {

  updateDistance();

  monitorForAutomaticBreakdown();

  if (
      buttonPressed(
          BTN_START,
          lastStartState
      )
  ) {

    startRoute();
  }

  if (
      buttonPressed(
          BTN_STOP,
          lastStopState
      )
  ) {

    normalStop();
  }

  if (
      buttonPressed(
          BTN_SOS,
          lastSOSState
      )
  ) {

    processDriverSOS();
  }

  delay(10);
}