from dataclasses import dataclass
from enum import Enum, auto


class LightMode(Enum):
    OFF = auto()
    GREEN_SOLID = auto()
    GREEN_BLINK_SLOW = auto()
    GREEN_BLINK = auto()
    YELLOW_SOLID = auto()
    YELLOW_BLINK_SLOW = auto()
    YELLOW_BLINK = auto()
    RED_SOLID = auto()
    RED_BLINK_SLOW = auto()
    RED_BLINK = auto()
    RED_GREEN_ALT = auto()
    RED_YELLOW_ALT = auto()
    YELLOW_GREEN_ALT = auto()
    RED_YELLOW_GREEN_ALT = auto()
    GREEN_YELLOW_RED_ALT = auto()
    ALL_ON = auto()
    ALL_BLINK_SLOW = auto()
    ALL_BLINK = auto()


@dataclass(frozen=True)
class LightOutput:
    red: bool
    yellow: bool
    green: bool


FLASHING_STEP_INITIAL_MS = 300
FLASHING_STEP_FLOOR_MS = 30
FLASHING_STEP_SPEEDUP_INTERVAL_MS = 1000


class LightController:
    def __init__(self) -> None:
        self._mode = LightMode.OFF
        self._mode_started_at_ms = 0

    @property
    def mode(self) -> LightMode:
        return self._mode

    def set_mode(self, mode: LightMode, now_ms: int = 0) -> None:
        self._mode = mode
        self._mode_started_at_ms = now_ms

    def render(self, now_ms: int) -> LightOutput:
        elapsed_ms = now_ms - self._mode_started_at_ms
        flashing_step = _flashing_step_ms(elapsed_ms)
        if self._mode is LightMode.OFF:
            return LightOutput(False, False, False)
        if self._mode is LightMode.GREEN_SOLID:
            return LightOutput(False, False, True)
        if self._mode is LightMode.GREEN_BLINK_SLOW:
            return LightOutput(False, False, _blink_phase(elapsed_ms, 1000))
        if self._mode is LightMode.GREEN_BLINK:
            return LightOutput(False, False, _blink_phase(elapsed_ms, flashing_step * 2))
        if self._mode is LightMode.YELLOW_SOLID:
            return LightOutput(False, True, False)
        if self._mode is LightMode.YELLOW_BLINK_SLOW:
            return LightOutput(False, _blink_phase(elapsed_ms, 1000), False)
        if self._mode is LightMode.YELLOW_BLINK:
            return LightOutput(False, _blink_phase(elapsed_ms, flashing_step * 2), False)
        if self._mode is LightMode.RED_SOLID:
            return LightOutput(True, False, False)
        if self._mode is LightMode.RED_BLINK_SLOW:
            return LightOutput(_blink_phase(elapsed_ms, 1000), False, False)
        if self._mode is LightMode.RED_BLINK:
            return LightOutput(_blink_phase(elapsed_ms, flashing_step * 2), False, False)
        if self._mode is LightMode.RED_GREEN_ALT:
            return _sequence_output(elapsed_ms, flashing_step, ["R", "G"])
        if self._mode is LightMode.RED_YELLOW_ALT:
            return _sequence_output(elapsed_ms, flashing_step, ["R", "Y"])
        if self._mode is LightMode.YELLOW_GREEN_ALT:
            return _sequence_output(elapsed_ms, flashing_step, ["Y", "G"])
        if self._mode is LightMode.RED_YELLOW_GREEN_ALT:
            return _sequence_output(elapsed_ms, flashing_step, ["R", "Y", "G"])
        if self._mode is LightMode.GREEN_YELLOW_RED_ALT:
            return _sequence_output(elapsed_ms, flashing_step, ["G", "Y", "R"])
        if self._mode is LightMode.ALL_ON:
            return LightOutput(True, True, True)
        if self._mode is LightMode.ALL_BLINK_SLOW:
            on = _blink_phase(elapsed_ms, 1000)
            return LightOutput(on, on, on)
        if self._mode is LightMode.ALL_BLINK:
            on = _blink_phase(elapsed_ms, flashing_step * 2)
            return LightOutput(on, on, on)
        raise AssertionError(f"Unhandled mode: {self._mode}")


def _blink_phase(now_ms: int, cycle_ms: int) -> bool:
    return (now_ms % cycle_ms) < (cycle_ms // 2)


def _flashing_step_ms(elapsed_ms: int) -> int:
    return max(FLASHING_STEP_FLOOR_MS, FLASHING_STEP_INITIAL_MS - (elapsed_ms // FLASHING_STEP_SPEEDUP_INTERVAL_MS))


def _state_output(state: str) -> LightOutput:
    return LightOutput("R" in state, "Y" in state, "G" in state)


def _sequence_output(now_ms: int, step_ms: int, states: list[str]) -> LightOutput:
    return _state_output(states[(now_ms // step_ms) % len(states)])


def apply_command(controller: LightController, command: str) -> bool:
    if command in ("\r", "\n"):
        return False

    mapping = {
        "A": LightMode.GREEN_SOLID,
        "C": LightMode.GREEN_BLINK_SLOW,
        "B": LightMode.GREEN_BLINK,
        "D": LightMode.YELLOW_SOLID,
        "F": LightMode.YELLOW_BLINK_SLOW,
        "E": LightMode.YELLOW_BLINK,
        "G": LightMode.RED_SOLID,
        "I": LightMode.RED_BLINK_SLOW,
        "H": LightMode.RED_BLINK,
        "J": LightMode.RED_GREEN_ALT,
        "L": LightMode.RED_YELLOW_ALT,
        "N": LightMode.YELLOW_GREEN_ALT,
        "Q": LightMode.RED_YELLOW_GREEN_ALT,
        "R": LightMode.GREEN_YELLOW_RED_ALT,
        "T": LightMode.OFF,
        "U": LightMode.ALL_ON,
        "W": LightMode.ALL_BLINK_SLOW,
        "V": LightMode.ALL_BLINK,
    }
    if command not in mapping:
        return False
    controller.set_mode(mapping[command])
    return True


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_all_known_commands_map_to_modes() -> None:
    controller = LightController()
    expected_modes = {
        "A": LightMode.GREEN_SOLID,
        "C": LightMode.GREEN_BLINK_SLOW,
        "B": LightMode.GREEN_BLINK,
        "D": LightMode.YELLOW_SOLID,
        "F": LightMode.YELLOW_BLINK_SLOW,
        "E": LightMode.YELLOW_BLINK,
        "G": LightMode.RED_SOLID,
        "I": LightMode.RED_BLINK_SLOW,
        "H": LightMode.RED_BLINK,
        "J": LightMode.RED_GREEN_ALT,
        "L": LightMode.RED_YELLOW_ALT,
        "N": LightMode.YELLOW_GREEN_ALT,
        "Q": LightMode.RED_YELLOW_GREEN_ALT,
        "R": LightMode.GREEN_YELLOW_RED_ALT,
        "T": LightMode.OFF,
        "U": LightMode.ALL_ON,
        "W": LightMode.ALL_BLINK_SLOW,
        "V": LightMode.ALL_BLINK,
    }

    for command, expected_mode in expected_modes.items():
        expect(apply_command(controller, command), f"{command} should be accepted")
        expect(controller.mode is expected_mode, f"{command} should map to {expected_mode}")


def test_invalid_input_is_ignored() -> None:
    controller = LightController()
    controller.set_mode(LightMode.RED_YELLOW_GREEN_ALT)

    expect(not apply_command(controller, "x"), "x should be rejected")
    expect(not apply_command(controller, "K"), "deprecated alias K should be rejected")
    expect(not apply_command(controller, "P"), "deprecated alias P should be rejected")
    expect(
        controller.mode is LightMode.RED_YELLOW_GREEN_ALT,
        "invalid input must not change mode",
    )


def test_line_endings_are_ignored() -> None:
    controller = LightController()
    controller.set_mode(LightMode.GREEN_SOLID)

    expect(not apply_command(controller, "\r"), "carriage return should be ignored")
    expect(controller.mode is LightMode.GREEN_SOLID, "carriage return must not change mode")

    expect(not apply_command(controller, "\n"), "newline should be ignored")
    expect(controller.mode is LightMode.GREEN_SOLID, "newline must not change mode")


def test_render_patterns() -> None:
    green_solid = LightController()
    green_solid.set_mode(LightMode.GREEN_SOLID)
    expect(green_solid.render(42) == LightOutput(False, False, True), "A should be green solid")

    yellow_blink = LightController()
    yellow_blink.set_mode(LightMode.YELLOW_BLINK, now_ms=0)
    expect(
        yellow_blink.render(0) == LightOutput(False, True, False),
        "E should start with yellow on",
    )
    expect(
        yellow_blink.render(300) == LightOutput(False, False, False),
        "E should turn yellow off after the initial step",
    )

    yellow_blink_slow = LightController()
    yellow_blink_slow.set_mode(LightMode.YELLOW_BLINK_SLOW, now_ms=0)
    expect(
        yellow_blink_slow.render(499) == LightOutput(False, True, False),
        "F should keep yellow on until the fixed slow half-cycle ends",
    )
    expect(
        yellow_blink_slow.render(500) == LightOutput(False, False, False),
        "F should switch yellow off at 500 ms",
    )

    red_green_alt = LightController()
    red_green_alt.set_mode(LightMode.RED_GREEN_ALT, now_ms=0)
    expect(
        red_green_alt.render(0) == LightOutput(True, False, False),
        "J should start on red",
    )
    expect(
        red_green_alt.render(300) == LightOutput(False, False, True),
        "J should switch to green on the next step",
    )

    three_color = LightController()
    three_color.set_mode(LightMode.RED_YELLOW_GREEN_ALT, now_ms=0)
    expect(three_color.render(0) == LightOutput(True, False, False), "Q should start red")
    expect(
        three_color.render(300) == LightOutput(False, True, False),
        "Q should move to yellow",
    )
    expect(
        three_color.render(600) == LightOutput(False, False, True),
        "Q should move to green",
    )

    reverse_three_color = LightController()
    reverse_three_color.set_mode(LightMode.GREEN_YELLOW_RED_ALT, now_ms=0)
    expect(
        reverse_three_color.render(0) == LightOutput(False, False, True),
        "R should start green",
    )
    expect(
        reverse_three_color.render(300) == LightOutput(False, True, False),
        "R should move to yellow",
    )
    expect(
        reverse_three_color.render(600) == LightOutput(True, False, False),
        "R should move to red",
    )

    all_on = LightController()
    all_on.set_mode(LightMode.ALL_ON)
    expect(all_on.render(10) == LightOutput(True, True, True), "U should light all lamps")

    all_blink = LightController()
    all_blink.set_mode(LightMode.ALL_BLINK, now_ms=0)
    expect(
        all_blink.render(0) == LightOutput(True, True, True),
        "V should start with all lamps on",
    )
    expect(
        all_blink.render(300) == LightOutput(False, False, False),
        "V should turn all lamps off after the initial step",
    )

    all_blink_slow = LightController()
    all_blink_slow.set_mode(LightMode.ALL_BLINK_SLOW, now_ms=0)
    expect(
        all_blink_slow.render(499) == LightOutput(True, True, True),
        "W should keep all lamps on until the fixed slow half-cycle ends",
    )
    expect(
        all_blink_slow.render(500) == LightOutput(False, False, False),
        "W should switch all lamps off at 500 ms",
    )

    accelerated_blink = LightController()
    accelerated_blink.set_mode(LightMode.GREEN_BLINK, now_ms=0)
    expect(
        accelerated_blink.render(1000 + 299) == LightOutput(False, False, True),
        "flashing schemes should speed up to 299 ms after one second",
    )

    floor_blink = LightController()
    floor_blink.set_mode(LightMode.GREEN_BLINK, now_ms=0)
    expect(
        floor_blink.render(270000 + 30) == LightOutput(False, False, False),
        "flashing schemes should stop accelerating at the 30 ms floor",
    )


def main() -> None:
    test_all_known_commands_map_to_modes()
    test_invalid_input_is_ignored()
    test_line_endings_are_ignored()
    test_render_patterns()
    print("PASS")


if __name__ == "__main__":
    main()
