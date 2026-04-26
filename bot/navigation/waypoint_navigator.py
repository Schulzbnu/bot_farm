from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from bot.core.models import NavigationConfig
from bot.perception.minimap_detector import DetectionResult, MinimapDetector


class KeyboardLike(Protocol):
    def tap(self, key: str, hold_seconds: float) -> None: ...


@dataclass(slots=True)
class MoveDecision:
    key: Optional[str]
    delta_x: int
    delta_y: int


class WaypointNavigator:
    """Converte posição relativa minimapa -> tecla de movimento no Tibia."""

    def __init__(
        self,
        config: NavigationConfig,
        detector: MinimapDetector,
        keyboard: KeyboardLike,
    ) -> None:
        self._config = config
        self._detector = detector
        self._keyboard = keyboard

    def tick(self) -> MoveDecision:
        detection = self._detector.detect()
        decision = self._decide(detection)
        if decision.key:
            self._keyboard.tap(decision.key, self._config.key_hold_seconds)
        return decision

    def _decide(self, detection: DetectionResult) -> MoveDecision:
        if detection.player is None or detection.waypoint is None:
            return MoveDecision(key=None, delta_x=0, delta_y=0)

        dx = detection.waypoint[0] - detection.player[0]
        dy = detection.waypoint[1] - detection.player[1]
        t = self._config.step_threshold_px

        if abs(dx) <= t and abs(dy) <= t:
            return MoveDecision(key=None, delta_x=dx, delta_y=dy)

        if abs(dx) >= abs(dy):
            return MoveDecision(key="d" if dx > 0 else "a", delta_x=dx, delta_y=dy)

        return MoveDecision(key="s" if dy > 0 else "w", delta_x=dx, delta_y=dy)
