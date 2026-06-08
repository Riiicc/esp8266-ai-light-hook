#include <ESP8266WiFi.h>
#include <stdint.h>

#include "light_protocol.h"

namespace {

constexpr char kSsid[] = "TP-LINK_2.4bbt";
constexpr char kPassword[] = "123584679";
constexpr uint16_t kPort = 8899;
constexpr uint32_t kClientIdleTimeoutMs = 1500U;

constexpr uint8_t kRedPin = D1;
constexpr uint8_t kYellowPin = D2;
constexpr uint8_t kGreenPin = D3;

IPAddress localIp(192, 168, 1, 88);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress dns(192, 168, 1, 1);

WiFiServer server(kPort);
WiFiClient activeClient;
LightController lightController;
bool hadClient = false;
uint32_t lastClientActivityMs = 0U;

void writePins(const LightOutput &output) {
  digitalWrite(kRedPin, output.red ? HIGH : LOW);
  digitalWrite(kYellowPin, output.yellow ? HIGH : LOW);
  digitalWrite(kGreenPin, output.green ? HIGH : LOW);
}

void updateLights() {
  writePins(lightController.render(millis()));
}

void logIpAddress() {
  IPAddress ip = WiFi.localIP();
  Serial.print(ip[0]);
  Serial.print('.');
  Serial.print(ip[1]);
  Serial.print('.');
  Serial.print(ip[2]);
  Serial.print('.');
  Serial.println(ip[3]);
}

void connectWifi() {
  WiFi.mode(WIFI_STA);

  if (!WiFi.config(localIp, gateway, subnet, dns)) {
    Serial.println("Static IP config failed");
  }

  WiFi.begin(kSsid, kPassword);
  lightController.setMode(LightMode::YellowBlink, millis());

  Serial.print("Connecting to WiFi: ");
  Serial.println(kSsid);

  while (WiFi.status() != WL_CONNECTED) {
    updateLights();
    delay(10);
  }

  Serial.print("WiFi connected, IP: ");
  logIpAddress();
}

void closeActiveClient(const char *reason) {
  if (!hadClient) {
    return;
  }

  activeClient.stop();
  hadClient = false;
  Serial.println(reason);
}

void acceptClientIfNeeded() {
  if (activeClient && activeClient.connected()) {
    if ((millis() - lastClientActivityMs) > kClientIdleTimeoutMs) {
      closeActiveClient("Client idle timeout");
    } else {
      return;
    }
  }

  if (hadClient) {
    closeActiveClient("Client disconnected");
    return;
  }

  WiFiClient incoming = server.available();
  if (incoming) {
    activeClient = incoming;
    hadClient = true;
    lastClientActivityMs = millis();
    Serial.print("Client connected from ");
    Serial.println(activeClient.remoteIP());
  }
}

void processClient() {
  if (!activeClient || !activeClient.connected()) {
    return;
  }

  while (activeClient.available() > 0) {
    char command = static_cast<char>(activeClient.read());
    lastClientActivityMs = millis();

    if (command == '\r' || command == '\n') {
      continue;
    }

    if (applyCommand(lightController, command, millis())) {
      activeClient.print("OK\n");
      Serial.print("Command accepted: ");
      Serial.println(command);
    } else {
      activeClient.print("ERR\n");
      Serial.print("Command rejected: ");
      Serial.println(command);
    }
  }
}

}  // namespace

void setup() {
  pinMode(kRedPin, OUTPUT);
  pinMode(kYellowPin, OUTPUT);
  pinMode(kGreenPin, OUTPUT);

  Serial.begin(115200);
  Serial.println();
  Serial.println("Booting ESP8266 AI Light Hook");

  lightController.setMode(LightMode::YellowBlink, millis());
  updateLights();

  connectWifi();
  server.begin();
  server.setNoDelay(true);

  Serial.print("TCP server listening on port ");
  Serial.println(kPort);

  lightController.setMode(LightMode::YellowBlink, millis());
}

void loop() {
  acceptClientIfNeeded();
  processClient();
  updateLights();
}
