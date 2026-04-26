from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import mss
import numpy as np


@dataclass(slots=True)
class CaptureRegion:
    left: int
    top: int
    width: int
    height: int

    def as_dict(self) -> Dict[str, int]:
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
        }


class ScreenCapture:
    def __init__(self) -> None:
        self._sct = mss.mss()

    def list_monitors(self) -> List[Dict[str, int]]:
        monitors = []
        for monitor in self._sct.monitors[1:]:
            monitors.append({k: int(monitor[k]) for k in ("left", "top", "width", "height")})
        return monitors

    def monitor_region(self, monitor_index: int) -> CaptureRegion:
        monitor = self._sct.monitors[monitor_index]
        return CaptureRegion(
            left=int(monitor["left"]),
            top=int(monitor["top"]),
            width=int(monitor["width"]),
            height=int(monitor["height"]),
        )

    def capture(self, region: CaptureRegion) -> np.ndarray:
        raw = self._sct.grab(region.as_dict())
        # BGRA -> BGR
        frame = np.array(raw)[:, :, :3]
        return frame

    def close(self) -> None:
        self._sct.close()


class DummyScreenCapture(ScreenCapture):
    """Helper para testes/manuais: retorna sempre o mesmo frame."""

    def __init__(self, frame: np.ndarray, monitors: Optional[List[Dict[str, int]]] = None) -> None:
        self._frame = frame
        self._monitors = monitors or [{"left": 0, "top": 0, "width": frame.shape[1], "height": frame.shape[0]}]

    def list_monitors(self) -> List[Dict[str, int]]:
        return self._monitors

    def capture(self, region: CaptureRegion) -> np.ndarray:
        return self._frame.copy()

    def close(self) -> None:
        return None
