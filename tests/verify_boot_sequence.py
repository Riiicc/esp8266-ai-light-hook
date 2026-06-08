from pathlib import Path


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    ino = Path("firmware/esp8266_ai_light_hook/esp8266_ai_light_hook.ino").read_text(encoding="utf-8")
    expect("kWifiConnectedBlinkCount = 5U" in ino, "WiFi success sequence must blink all lights five times")
    expect("kWifiConnectedBlinkStepMs = 150U" in ino, "WiFi success sequence must define a fixed blink step")
    expect("blinkAllLights(kWifiConnectedBlinkCount, kWifiConnectedBlinkStepMs);" in ino,
           "WiFi success sequence must run after the device connects")
    print("PASS")


if __name__ == "__main__":
    main()
