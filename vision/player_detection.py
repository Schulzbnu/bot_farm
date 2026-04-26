from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np


@dataclass(slots=True)
class DetectionResult:
    position: Optional[Tuple[int, int]]
    confidence: float


class PlayerDetector:
    def __init__(self, template_path: str, min_confidence: float = 0.65) -> None:
        self.template = cv2.imread(str(Path(template_path)), cv2.IMREAD_COLOR)
        if self.template is None:
            raise FileNotFoundError(f"Template não encontrado: {template_path}")
        self.template_h, self.template_w = self.template.shape[:2]
        self.min_confidence = min_confidence

    def detect(self, frame: np.ndarray) -> DetectionResult:
        result = cv2.matchTemplate(frame, self.template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val < self.min_confidence:
            return DetectionResult(position=None, confidence=float(max_val))

        center_x = max_loc[0] + self.template_w // 2
        center_y = max_loc[1] + self.template_h // 2
        return DetectionResult(position=(center_x, center_y), confidence=float(max_val))
