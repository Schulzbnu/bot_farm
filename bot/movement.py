from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from bot.models import Coordinate, WaypointList


@dataclass
class MovementState:
    is_running: bool = False
    current_position: Coordinate = field(default_factory=lambda: Coordinate(0, 0, 0))
    current_waypoint_index: int = 0


class MovementController:
    """
    Controlador de movimentação em grid para cavehunting.

    MVP atual:
    - Movimenta 1 tile por ciclo em direção ao waypoint atual.
    - Quando alcança, avança para o próximo waypoint em loop.
    - Fornece callback para UI acompanhar estado em tempo real.
    """

    def __init__(self, tick_interval: float = 0.3) -> None:
        self.tick_interval = tick_interval
        self.state = MovementState()
        self._waypoints: WaypointList = []
        self._on_state_update: Optional[Callable[[MovementState], None]] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def set_waypoints(self, waypoints: WaypointList) -> None:
        with self._lock:
            self._waypoints = waypoints
            self.state.current_waypoint_index = 0

    def set_current_position(self, coordinate: Coordinate) -> None:
        with self._lock:
            self.state.current_position = coordinate
            self._notify()

    def on_state_update(self, callback: Callable[[MovementState], None]) -> None:
        self._on_state_update = callback

    def start(self) -> None:
        with self._lock:
            if self.state.is_running:
                return
            if not self._waypoints:
                raise ValueError("Defina ao menos um waypoint antes de iniciar.")
            self.state.is_running = True
            self._stop_event.clear()

        self._thread = threading.Thread(target=self._movement_loop, daemon=True)
        self._thread.start()
        self._notify()

    def stop(self) -> None:
        with self._lock:
            if not self.state.is_running:
                return
            self.state.is_running = False
            self._stop_event.set()

        self._notify()

    def nearest_waypoint(self) -> Optional[Coordinate]:
        with self._lock:
            if not self._waypoints:
                return None

            current = self.state.current_position
            return min(
                self._waypoints,
                key=lambda wp: abs(wp.x - current.x) + abs(wp.y - current.y) + abs(wp.z - current.z),
            )

    def current_target_waypoint(self) -> Optional[Coordinate]:
        with self._lock:
            if not self._waypoints:
                return None
            return self._waypoints[self.state.current_waypoint_index]

    def _movement_loop(self) -> None:
        while not self._stop_event.is_set():
            with self._lock:
                if not self.state.is_running or not self._waypoints:
                    break

                target = self._waypoints[self.state.current_waypoint_index]
                current = self.state.current_position

                next_step = self._move_one_tile(current, target)
                self.state.current_position = next_step

                if next_step == target:
                    self.state.current_waypoint_index = (self.state.current_waypoint_index + 1) % len(self._waypoints)

                self._notify()

            time.sleep(self.tick_interval)

    def _move_one_tile(self, current: Coordinate, target: Coordinate) -> Coordinate:
        next_x = current.x
        next_y = current.y
        next_z = current.z

        if current.z != target.z:
            next_z += 1 if target.z > current.z else -1
            return Coordinate(next_x, next_y, next_z)

        if current.x != target.x:
            next_x += 1 if target.x > current.x else -1
            return Coordinate(next_x, next_y, next_z)

        if current.y != target.y:
            next_y += 1 if target.y > current.y else -1

        return Coordinate(next_x, next_y, next_z)

    def _notify(self) -> None:
        if self._on_state_update:
            snapshot = MovementState(
                is_running=self.state.is_running,
                current_position=self.state.current_position,
                current_waypoint_index=self.state.current_waypoint_index,
            )
            self._on_state_update(snapshot)


def parse_waypoint_lines(raw_lines: str) -> List[Coordinate]:
    """
    Formato por linha:
    x,y,z

    Exemplo:
    100,200,7
    101,201,7
    """

    waypoints: List[Coordinate] = []
    for idx, line in enumerate(raw_lines.splitlines(), start=1):
        normalized = line.strip()
        if not normalized:
            continue

        parts = [p.strip() for p in normalized.split(",")]
        if len(parts) != 3:
            raise ValueError(f"Linha {idx}: esperado formato x,y,z")

        x, y, z = map(int, parts)
        waypoints.append(Coordinate(x, y, z))

    if not waypoints:
        raise ValueError("Nenhum waypoint válido informado.")

    return waypoints
