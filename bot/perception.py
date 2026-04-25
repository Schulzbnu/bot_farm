from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional

from bot.models import Coordinate, ProfileConfig, ScreenRegion
from bot.movement import MovementController

try:
    import cv2  # type: ignore
    import mss  # type: ignore
    import numpy as np
except ImportError:  # pragma: no cover - depende de ambiente local
    cv2 = None
    mss = None
    np = None


@dataclass
class PerceptionSettings:
    region_name: str = "minimap"
    origin_x: int = 100
    origin_y: int = 100
    origin_z: int = 7
    tile_size_px: float = 8.0
    marker_h_min: int = 0
    marker_s_min: int = 0
    marker_v_min: int = 220
    marker_h_max: int = 179
    marker_s_max: int = 45
    marker_v_max: int = 255
    fps: float = 4.0


@dataclass
class PerceptionState:
    is_running: bool = False
    last_coordinate: Coordinate | None = None
    last_marker_px: tuple[int, int] | None = None
    message: str = "Percepção parada"


class ScreenPerceptionService:
    """
    Integração de percepção real de tela.

    Estratégia atual:
    - Captura a região configurada (ex.: minimap) com mss.
    - Detecta marcador do player por faixa HSV.
    - Converte pixel -> coordenada de tile via calibração simples.
    - Publica coordenada para o MovementController.
    """

    def __init__(self, profile: ProfileConfig, controller: MovementController) -> None:
        self.profile = profile
        self.controller = controller
        self.settings = PerceptionSettings()
        self.state = PerceptionState()
        self._on_state: Optional[Callable[[PerceptionState], None]] = None

        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    @staticmethod
    def dependencies_available() -> bool:
        return bool(cv2 and mss and np)

    def on_state_update(self, callback: Callable[[PerceptionState], None]) -> None:
        self._on_state = callback

    def configure(self, settings: PerceptionSettings) -> None:
        with self._lock:
            self.settings = settings

    def start(self) -> None:
        if not self.dependencies_available():
            raise RuntimeError("Dependências ausentes: instale mss, numpy e opencv-python.")

        with self._lock:
            if self.state.is_running:
                return
            if not self.profile.get_region(self.settings.region_name):
                raise ValueError(
                    f"Região '{self.settings.region_name}' não encontrada. Cadastre em 'Regiões necessárias'."
                )

            self.state.is_running = True
            self.state.message = "Percepção ativa"
            self._stop_event.clear()

        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        self._notify()

    def stop(self) -> None:
        with self._lock:
            self.state.is_running = False
            self.state.message = "Percepção parada"
            self._stop_event.set()

        self._notify()

    def _loop(self) -> None:
        frame_interval = 1.0 / max(self.settings.fps, 0.5)

        while not self._stop_event.is_set():
            started_at = time.time()
            region = self.profile.get_region(self.settings.region_name)
            if region is None:
                with self._lock:
                    self.state.message = f"Região '{self.settings.region_name}' ausente"
                self._notify()
                break

            coord, marker_px = self._capture_and_estimate_coordinate(region, self.settings)
            with self._lock:
                self.state.last_coordinate = coord
                self.state.last_marker_px = marker_px
                self.state.message = "Percepção ativa" if coord else "Marcador não detectado"

            if coord is not None:
                self.controller.set_current_position(coord)

            self._notify()

            elapsed = time.time() - started_at
            to_sleep = max(0.0, frame_interval - elapsed)
            time.sleep(to_sleep)

    def _capture_and_estimate_coordinate(
        self,
        region: ScreenRegion,
        settings: PerceptionSettings,
    ) -> tuple[Coordinate | None, tuple[int, int] | None]:
        assert mss and cv2 and np

        monitor = {
            "top": region.y,
            "left": region.x,
            "width": region.width,
            "height": region.height,
        }

        with mss.mss() as capture:
            frame = capture.grab(monitor)

        image = np.array(frame)
        bgr = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

        low = np.array([settings.marker_h_min, settings.marker_s_min, settings.marker_v_min], dtype=np.uint8)
        high = np.array([settings.marker_h_max, settings.marker_s_max, settings.marker_v_max], dtype=np.uint8)
        mask = cv2.inRange(hsv, low, high)

        moments = cv2.moments(mask)
        if moments["m00"] <= 0:
            return None, None

        marker_x = int(moments["m10"] / moments["m00"])
        marker_y = int(moments["m01"] / moments["m00"])

        center_x = region.width // 2
        center_y = region.height // 2

        delta_tiles_x = round((marker_x - center_x) / settings.tile_size_px)
        delta_tiles_y = round((marker_y - center_y) / settings.tile_size_px)

        coord = Coordinate(
            x=settings.origin_x + delta_tiles_x,
            y=settings.origin_y + delta_tiles_y,
            z=settings.origin_z,
        )

        return coord, (marker_x, marker_y)

    def _notify(self) -> None:
        if self._on_state:
            snapshot = PerceptionState(
                is_running=self.state.is_running,
                last_coordinate=self.state.last_coordinate,
                last_marker_px=self.state.last_marker_px,
                message=self.state.message,
            )
            self._on_state(snapshot)
