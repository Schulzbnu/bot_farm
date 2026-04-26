from bot.core.models import NavigationConfig, ScreenRegion
from bot.navigation.waypoint_navigator import WaypointNavigator
from bot.perception.minimap_detector import DetectionResult


class DummyDetector:
    def __init__(self, result: DetectionResult):
        self._result = result

    def detect(self):
        return self._result


class DummyKeyboard:
    def __init__(self):
        self.taps = []

    def tap(self, key: str, hold_seconds: float) -> None:
        self.taps.append((key, hold_seconds))


def make_config() -> NavigationConfig:
    region = ScreenRegion(0, 0, 100, 100)
    return NavigationConfig(game_region=region, minimap_region=region, step_threshold_px=4)


def test_move_horizontal_priority_when_dx_bigger() -> None:
    detector = DummyDetector(DetectionResult(player=(10, 10), waypoint=(20, 13)))
    keyboard = DummyKeyboard()
    nav = WaypointNavigator(make_config(), detector, keyboard)

    decision = nav.tick()

    assert decision.key == "d"
    assert keyboard.taps[0][0] == "d"


def test_stop_when_close_to_waypoint() -> None:
    detector = DummyDetector(DetectionResult(player=(10, 10), waypoint=(12, 11)))
    keyboard = DummyKeyboard()
    nav = WaypointNavigator(make_config(), detector, keyboard)

    decision = nav.tick()

    assert decision.key is None
    assert keyboard.taps == []
