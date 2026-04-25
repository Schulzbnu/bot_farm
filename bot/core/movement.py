from __future__ import annotations

from dataclasses import dataclass, field

from .pathfinding import Coordinate, MapGrid, astar_path


@dataclass
class Waypoint:
    label: str
    coordinate: Coordinate
    type: str = "walk"
    ignore: bool = False
    passinho: bool = False


@dataclass
class MovementState:
    position: Coordinate
    current_waypoint_index: int = 0
    current_segment_path: list[Coordinate] = field(default_factory=list)
    path_cursor: int = 0
    finished: bool = False


class MovementEngine:
    def __init__(self, grid: MapGrid, waypoints: list[Waypoint], start: Coordinate):
        if not waypoints:
            raise ValueError("Informe pelo menos 1 waypoint")
        self.grid = grid
        self.waypoints = waypoints
        self.state = MovementState(position=start)

    def _target_waypoint(self) -> Waypoint:
        return self.waypoints[self.state.current_waypoint_index]

    def _rebuild_segment(self) -> None:
        target = self._target_waypoint().coordinate
        self.state.current_segment_path = astar_path(self.grid, self.state.position, target)
        self.state.path_cursor = 0

    def step(self) -> MovementState:
        if self.state.finished:
            return self.state

        if not self.state.current_segment_path:
            self._rebuild_segment()

        if not self.state.current_segment_path:
            self.state.finished = True
            return self.state

        # Posição 0 do path é o tile atual
        if self.state.path_cursor < len(self.state.current_segment_path) - 1:
            self.state.path_cursor += 1
            self.state.position = self.state.current_segment_path[self.state.path_cursor]
            return self.state

        # Waypoint alcançado -> próximo
        self.state.current_waypoint_index += 1
        if self.state.current_waypoint_index >= len(self.waypoints):
            self.state.finished = True
            return self.state

        self.state.current_segment_path = []
        self.state.path_cursor = 0
        return self.state

    def reset(self, start: Coordinate | None = None) -> None:
        self.state.position = start if start else self.state.position
        self.state.current_waypoint_index = 0
        self.state.current_segment_path = []
        self.state.path_cursor = 0
        self.state.finished = False
