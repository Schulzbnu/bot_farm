from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from typing import Iterable


@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int
    z: int = 0


@dataclass
class MapGrid:
    width: int
    height: int
    floor: int = 0
    blocked: set[tuple[int, int]] | None = None

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width/height devem ser > 0")
        if self.blocked is None:
            self.blocked = set()

    def is_inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, x: int, y: int) -> bool:
        return self.is_inside(x, y) and (x, y) not in self.blocked


def manhattan(a: Coordinate, b: Coordinate) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def neighbors(grid: MapGrid, node: Coordinate) -> Iterable[Coordinate]:
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = node.x + dx, node.y + dy
        if grid.is_walkable(nx, ny):
            yield Coordinate(nx, ny, node.z)


def astar_path(grid: MapGrid, start: Coordinate, goal: Coordinate) -> list[Coordinate]:
    if start.z != goal.z:
        raise ValueError("MVP suporta apenas path no mesmo andar (z)")
    if not grid.is_walkable(start.x, start.y):
        raise ValueError("posição inicial bloqueada")
    if not grid.is_walkable(goal.x, goal.y):
        raise ValueError("posição de destino bloqueada")

    frontier: list[tuple[int, int, Coordinate]] = []
    came_from: dict[Coordinate, Coordinate | None] = {start: None}
    g_score: dict[Coordinate, int] = {start: 0}
    seq = 0
    heappush(frontier, (manhattan(start, goal), seq, start))

    while frontier:
        _, _, current = heappop(frontier)
        if current == goal:
            break

        for nxt in neighbors(grid, current):
            tentative = g_score[current] + 1
            if tentative < g_score.get(nxt, 10**9):
                came_from[nxt] = current
                g_score[nxt] = tentative
                seq += 1
                priority = tentative + manhattan(nxt, goal)
                heappush(frontier, (priority, seq, nxt))

    if goal not in came_from:
        return []

    rev: list[Coordinate] = []
    cur: Coordinate | None = goal
    while cur is not None:
        rev.append(cur)
        cur = came_from[cur]
    rev.reverse()
    return rev
