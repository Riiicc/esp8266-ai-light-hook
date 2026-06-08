#include <cstdlib>
#include <iostream>
#include <string>

#include "../firmware/esp8266_ai_light_hook/light_protocol.h"

namespace {

void expect(bool condition, const std::string &message) {
  if (!condition) {
    std::cerr << "FAIL: " << message << std::endl;
    std::exit(1);
  }
}

void test_known_commands_map_to_modes() {
  LightController controller;

  expect(applyCommand(controller, 'A', 0U), "A should be accepted");
  expect(controller.mode() == LightMode::GreenSolid, "A should select green solid");

  expect(applyCommand(controller, 'C', 0U), "C should be accepted");
  expect(controller.mode() == LightMode::GreenBlinkSlow, "C should select green slow blink");

  expect(applyCommand(controller, 'E', 0U), "E should be accepted");
  expect(controller.mode() == LightMode::RedYellowGreenAltFixed, "E should select fixed three-color alternate");

  expect(applyCommand(controller, 'F', 0U), "F should be accepted");
  expect(controller.mode() == LightMode::YellowBlinkSlow, "F should select yellow slow blink");

  expect(applyCommand(controller, 'J', 0U), "J should be accepted");
  expect(controller.mode() == LightMode::RedGreenAlt, "J should select red-green alternate");

  expect(applyCommand(controller, 'Q', 0U), "Q should be accepted");
  expect(controller.mode() == LightMode::RedYellowGreenAlt, "Q should select three-color alternate");

  expect(applyCommand(controller, 'T', 0U), "T should be accepted");
  expect(controller.mode() == LightMode::Off, "T should switch all lamps off");

  expect(applyCommand(controller, 'V', 0U), "V should be accepted");
  expect(controller.mode() == LightMode::AllBlink, "V should select all blink");

  expect(applyCommand(controller, 'W', 0U), "W should be accepted");
  expect(controller.mode() == LightMode::AllBlinkSlow, "W should select all slow blink");
}

}  // namespace

int main() {
  test_known_commands_map_to_modes();
  std::cout << "PASS" << std::endl;
  return 0;
}
