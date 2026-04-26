from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cv2
import mss
import numpy as np

from bot.core.models import NavigationConfig


@dataclass(slots=True)
class DetectionResult:
    player: Optional[tuple[int, int]]
    waypoint: Optional[tuple[int, int]]


class MinimapDetector:
    """Detecta marcador do player e waypoint pela cor no minimapa."""

    def __init__(self, config: NavigationConfig) -> None:
        self._config = config

    def capture_minimap(self) -> np.ndarray:
        with mss.mss() as sct:
            shot = sct.grab(self._config.minimap_region.to_mss())
            return np.array(shot)[:, :, :3]

    def detect(self, frame_bgr: np.ndarray | None = None) -> DetectionResult:
        frame = self.capture_minimap() if frame_bgr is None else frame_bgr
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        player_mask = cv2.inRange(
            hsv,
            np.array(self._config.player_hsv_low, dtype=np.uint8),
            np.array(self._config.player_hsv_high, dtype=np.uint8),
        )
        waypoint_mask = cv2.inRange(
            hsv,
            np.array(self._config.waypoint_hsv_low, dtype=np.uint8),
            np.array(self._config.waypoint_hsv_high, dtype=np.uint8),
        )

        return DetectionResult(
            player=self._largest_centroid(player_mask),
            waypoint=self._largest_centroid(waypoint_mask),
        )

    @staticmethod
    def _largest_centroid(mask: np.ndarray) -> Optional[tuple[int, int]]:
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        contour = max(contours, key=cv2.contourArea)
        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            return None

        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])
        return cx, cy
