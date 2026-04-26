from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from navigation.waypoints import Waypoint


@dataclass(slots=True)
class Direction:
    horizontal: Optional[str]
    vertical: Optional[str]


class PathExecutor:
    def __init__(self, waypoints: list[Waypoint], tolerance: int = 6) -> None:
        self.waypoints = waypoints
        self.tolerance = tolerance
        self.current_idx = 0

    @property
    def current_waypoint(self) -> Waypoint:
        return self.waypoints[self.current_idx]

    def advance_if_reached(self, x: int, y: int) -> bool:
        wp = self.current_waypoint
        if abs(wp.x - x) <= self.tolerance and abs(wp.y - y) <= self.tolerance:
            self.current_idx = (self.current_idx + 1) % len(self.waypoints)
            return True
        return False

    def direction_to_waypoint(self, x: int, y: int) -> Direction:
        wp = self.current_waypoint
        horizontal = None
        vertical = None
        if abs(wp.x - x) > self.tolerance:
            horizontal = "right" if wp.x > x else "left"
        if abs(wp.y - y) > self.tolerance:
            vertical = "down" if wp.y > y else "up"
        return Direction(horizontal=horizontal, vertical=vertical)
