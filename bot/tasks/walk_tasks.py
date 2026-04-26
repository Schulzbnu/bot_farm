from __future__ import annotations

from dataclasses import dataclass
from time import sleep

from bot.input.keyboard import KeyboardController
from bot.navigation.pathfinding import generateFloorWalkpoints
from bot.navigation.radar import Coordinate

_DIRECTION_KEYS = {
    (1, 0): "right",
    (-1, 0): "left",
    (0, 1): "down",
    (0, -1): "up",
}


@dataclass(slots=True)
class CharacterStats:
    speed: int = 220
    tile_friction_ms: int = 60


def getDirectionBetweenCoordinates(current: Coordinate, nxt: Coordinate) -> str:
    delta = (nxt[0] - current[0], nxt[1] - current[1])
    if delta not in _DIRECTION_KEYS:
        raise ValueError(f"Movimento inválido entre {current} -> {nxt}")
    return _DIRECTION_KEYS[delta]


@dataclass(slots=True)
class WalkTask:
    current: Coordinate
    next_waypoint: Coordinate
    keyboard: KeyboardController
    stats: CharacterStats

    def run(self) -> None:
        direction = getDirectionBetweenCoordinates(self.current, self.next_waypoint)
        hold_multiplier = max(0.8, 220 / max(self.stats.speed, 120))
        self.keyboard.tap(direction, hold_multiplier=hold_multiplier)
        sleep(self.stats.tile_friction_ms / 1000)


@dataclass(slots=True)
class WalkToWaypointTask:
    current: Coordinate
    waypoints: list[Coordinate]
    keyboard: KeyboardController
    stats: CharacterStats

    def run(self) -> None:
        position = self.current
        for waypoint in self.waypoints:
            WalkTask(position, waypoint, self.keyboard, self.stats).run()
            position = waypoint


@dataclass(slots=True)
class WalkToCoordinateTask:
    current: Coordinate
    goal: Coordinate
    non_walkable_coordinates: list[Coordinate]
    keyboard: KeyboardController
    stats: CharacterStats

    def calculateWalkpoint(self) -> list[Coordinate]:
        return generateFloorWalkpoints(self.current, self.goal, self.non_walkable_coordinates)

    def run(self) -> None:
        walkpoints = self.calculateWalkpoint()
        WalkToWaypointTask(self.current, walkpoints, self.keyboard, self.stats).run()
