from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Optional

from input.keyboard_controller import KeyboardController
from navigation.path_executor import PathExecutor
from vision.player_detection import PlayerDetector
from vision.screen_capture import CaptureRegion, ScreenCapture


@dataclass(slots=True)
class BotStatus:
    running: bool = False
    last_confidence: float = 0.0
    last_position: Optional[tuple[int, int]] = None


class BotEngine:
    def __init__(
        self,
        capture: ScreenCapture,
        detector: PlayerDetector,
        path_executor: PathExecutor,
        keyboard: KeyboardController,
        region: CaptureRegion,
        tick_seconds: float = 0.1,
    ) -> None:
        self.capture = capture
        self.detector = detector
        self.path_executor = path_executor
        self.keyboard = keyboard
        self.region = region
        self.tick_seconds = tick_seconds
        self.status = BotStatus()
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        if self.status.running:
            return
        self._stop_event.clear()
        self.status.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self.status.running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            frame = self.capture.capture(self.region)
            detection = self.detector.detect(frame)
            self.status.last_confidence = detection.confidence
            self.status.last_position = detection.position

            if detection.position:
                x, y = detection.position
                self.path_executor.advance_if_reached(x, y)
                direction = self.path_executor.direction_to_waypoint(x, y)
                self.keyboard.move_step(direction.horizontal, direction.vertical)

            time.sleep(self.tick_seconds)
