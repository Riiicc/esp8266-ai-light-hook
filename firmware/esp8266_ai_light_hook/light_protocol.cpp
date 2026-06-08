#include "light_protocol.h"

namespace {

constexpr uint32_t kFlashingStepInitialMs = 300U;
constexpr uint32_t kFlashingStepFloorMs = 30U;
constexpr uint32_t kFlashingStepSpeedupIntervalMs = 1000U;
constexpr uint32_t kSlowBlinkStepMs = 500U;

LightOutput offOutput() { return {false, false, false}; }

bool blinkPhase(uint32_t nowMs, uint32_t cycleMs) {
  return (nowMs % cycleMs) < (cycleMs / 2U);
}

LightOutput stateOutput(char state) {
  return {state == 'R', state == 'Y', state == 'G'};
}

uint32_t flashingStepMs(uint32_t elapsedMs) {
  uint32_t reduction = elapsedMs / kFlashingStepSpeedupIntervalMs;
  if (reduction >= (kFlashingStepInitialMs - kFlashingStepFloorMs)) {
    return kFlashingStepFloorMs;
  }

  uint32_t currentStepMs = kFlashingStepInitialMs - reduction;
  if (currentStepMs < kFlashingStepFloorMs) {
    return kFlashingStepFloorMs;
  }
  return currentStepMs;
}

LightOutput sequenceOutput(uint32_t elapsedMs, uint32_t stepMs, const char *states,
                           uint32_t stateCount) {
  return stateOutput(states[(elapsedMs / stepMs) % stateCount]);
}

}  // namespace

LightController::LightController() : mode_(LightMode::Off), modeStartedAtMs_(0U) {}

LightMode LightController::mode() const { return mode_; }

void LightController::setMode(LightMode nextMode, uint32_t nowMs) {
  mode_ = nextMode;
  modeStartedAtMs_ = nowMs;
}

LightOutput LightController::render(uint32_t nowMs) const {
  uint32_t elapsedMs = nowMs - modeStartedAtMs_;
  uint32_t flashingStep = flashingStepMs(elapsedMs);

  switch (mode_) {
    case LightMode::Off:
      return offOutput();
    case LightMode::GreenSolid:
      return {false, false, true};
    case LightMode::GreenBlinkSlow:
      return {false, false, blinkPhase(elapsedMs, kSlowBlinkStepMs * 2U)};
    case LightMode::GreenBlink:
      return {false, false, blinkPhase(elapsedMs, flashingStep * 2U)};
    case LightMode::YellowSolid:
      return {false, true, false};
    case LightMode::YellowBlinkSlow:
      return {false, blinkPhase(elapsedMs, kSlowBlinkStepMs * 2U), false};
    case LightMode::YellowBlink:
      return {false, blinkPhase(elapsedMs, flashingStep * 2U), false};
    case LightMode::RedSolid:
      return {true, false, false};
    case LightMode::RedBlinkSlow:
      return {blinkPhase(elapsedMs, kSlowBlinkStepMs * 2U), false, false};
    case LightMode::RedBlink:
      return {blinkPhase(elapsedMs, flashingStep * 2U), false, false};
    case LightMode::RedGreenAlt:
      return sequenceOutput(elapsedMs, flashingStep, "RG", 2U);
    case LightMode::RedYellowAlt:
      return sequenceOutput(elapsedMs, flashingStep, "RY", 2U);
    case LightMode::YellowGreenAlt:
      return sequenceOutput(elapsedMs, flashingStep, "YG", 2U);
    case LightMode::RedYellowGreenAlt:
      return sequenceOutput(elapsedMs, flashingStep, "RYG", 3U);
    case LightMode::GreenYellowRedAlt:
      return sequenceOutput(elapsedMs, flashingStep, "GYR", 3U);
    case LightMode::AllOn:
      return {true, true, true};
    case LightMode::AllBlinkSlow: {
      bool on = blinkPhase(elapsedMs, kSlowBlinkStepMs * 2U);
      return {on, on, on};
    }
    case LightMode::AllBlink: {
      bool on = blinkPhase(elapsedMs, flashingStep * 2U);
      return {on, on, on};
    }
    default:
      return offOutput();
  }
}

bool applyCommand(LightController &controller, char command, uint32_t nowMs) {
  if (command == '\r' || command == '\n') {
    return false;
  }

  switch (command) {
    case 'A':
      controller.setMode(LightMode::GreenSolid, nowMs);
      return true;
    case 'B':
      controller.setMode(LightMode::GreenBlink, nowMs);
      return true;
    case 'C':
      controller.setMode(LightMode::GreenBlinkSlow, nowMs);
      return true;
    case 'D':
      controller.setMode(LightMode::YellowSolid, nowMs);
      return true;
    case 'E':
      controller.setMode(LightMode::YellowBlink, nowMs);
      return true;
    case 'F':
      controller.setMode(LightMode::YellowBlinkSlow, nowMs);
      return true;
    case 'G':
      controller.setMode(LightMode::RedSolid, nowMs);
      return true;
    case 'H':
      controller.setMode(LightMode::RedBlink, nowMs);
      return true;
    case 'I':
      controller.setMode(LightMode::RedBlinkSlow, nowMs);
      return true;
    case 'J':
      controller.setMode(LightMode::RedGreenAlt, nowMs);
      return true;
    case 'L':
      controller.setMode(LightMode::RedYellowAlt, nowMs);
      return true;
    case 'N':
      controller.setMode(LightMode::YellowGreenAlt, nowMs);
      return true;
    case 'Q':
      controller.setMode(LightMode::RedYellowGreenAlt, nowMs);
      return true;
    case 'R':
      controller.setMode(LightMode::GreenYellowRedAlt, nowMs);
      return true;
    case 'T':
      controller.setMode(LightMode::Off, nowMs);
      return true;
    case 'U':
      controller.setMode(LightMode::AllOn, nowMs);
      return true;
    case 'V':
      controller.setMode(LightMode::AllBlink, nowMs);
      return true;
    case 'W':
      controller.setMode(LightMode::AllBlinkSlow, nowMs);
      return true;
    default:
      return false;
  }
}
