#pragma once

#include <stdint.h>

enum class LightMode {
  Off,
  GreenSolid,
  GreenBlinkSlow,
  GreenBlink,
  YellowSolid,
  YellowBlinkSlow,
  YellowBlink,
  RedSolid,
  RedBlinkSlow,
  RedBlink,
  RedGreenAlt,
  RedYellowAlt,
  YellowGreenAlt,
  RedYellowGreenAlt,
  GreenYellowRedAlt,
  AllOn,
  AllBlinkSlow,
  AllBlink,
};

struct LightOutput {
  bool red;
  bool yellow;
  bool green;
};

class LightController {
 public:
  LightController();

  LightMode mode() const;
  void setMode(LightMode nextMode, uint32_t nowMs);
  LightOutput render(uint32_t nowMs) const;

 private:
  LightMode mode_;
  uint32_t modeStartedAtMs_;
};

bool applyCommand(LightController &controller, char command, uint32_t nowMs);
