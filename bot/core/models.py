from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(slots=True)
class ScreenRegion:
    """Região da tela capturada pelo bot."""

    left: int
    top: int
    width: int
    height: int

    def to_mss(self) -> dict[str, int]:
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
        }


@dataclass(slots=True)
class NavigationConfig:
    """Configuração mínima de navegação por waypoint."""

    game_region: ScreenRegion
    minimap_region: ScreenRegion
    waypoint_hsv_low: Tuple[int, int, int] = (20, 150, 150)
    waypoint_hsv_high: Tuple[int, int, int] = (40, 255, 255)
    player_hsv_low: Tuple[int, int, int] = (0, 150, 150)
    player_hsv_high: Tuple[int, int, int] = (10, 255, 255)
    step_threshold_px: int = 6
    key_hold_seconds: float = 0.08
