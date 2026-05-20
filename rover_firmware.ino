#include <WiFi.h>

// ── WiFi credentials ─────────────────────────────────────────────────────────
// WARNING: Replace these before flashing. Do NOT commit real credentials to
// version control. Consider storing them in a secrets.h excluded via .gitignore.
const char* WIFI_SSID     = "YOUR_SSID";
const char* WIFI_PASSWORD = "YOUR_PASSWORD";

// Reconnection settings
static const uint32_t WIFI_CONNECT_TIMEOUT_MS = 15000;  // 15 s
static const uint32_t WIFI_RETRY_INTERVAL_MS  =  5000;  //  5 s

// ── Forward declarations ──────────────────────────────────────────────────────
static void connectToWiFi();
static void printWiFiStatus();

// ── setup() ──────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  // Wait up to 2 s for USB-Serial; skip on boards without native USB
  uint32_t serialWait = millis();
  while (!Serial && (millis() - serialWait < 2000)) { ; }

  Serial.println("\n=== Semi-Autonomous Rover Firmware ===");

  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);   // reconnect automatically after a drop
  connectToWiFi();
}

// ── loop() ───────────────────────────────────────────────────────────────────
void loop() {
  static uint32_t lastReconnectAttempt = 0;

  // Re-attempt connection if it was lost, but only every WIFI_RETRY_INTERVAL_MS
  if (WiFi.status() != WL_CONNECTED) {
    uint32_t now = millis();
    if (now - lastReconnectAttempt >= WIFI_RETRY_INTERVAL_MS) {
      lastReconnectAttempt = now;
      Serial.println("[WiFi] Connection lost. Reconnecting…");
      connectToWiFi();
    }
  }

  // TODO: add rover control / sensor logic here
  delay(100);
}

// ── helpers ──────────────────────────────────────────────────────────────────

// Block until connected or timeout, then print status.
static void connectToWiFi() {
  Serial.printf("[WiFi] Connecting to \"%s\"", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  uint32_t start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - start >= WIFI_CONNECT_TIMEOUT_MS) {
      Serial.println("\n[WiFi] Connection timed out. Will retry later.");
      return;
    }
    delay(500);
    Serial.print('.');
  }

  Serial.println();
  printWiFiStatus();
}

// Print IP address, gateway and signal strength.
static void printWiFiStatus() {
  Serial.println("[WiFi] Connected!");
  Serial.print  ("       SSID    : "); Serial.println(WiFi.SSID());
  Serial.print  ("       IP      : "); Serial.println(WiFi.localIP());
  Serial.print  ("       Gateway : "); Serial.println(WiFi.gatewayIP());
  Serial.print  ("       RSSI    : "); Serial.print(WiFi.RSSI()); Serial.println(" dBm");
}
