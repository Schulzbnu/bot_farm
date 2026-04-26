from __future__ import annotations

from collections.abc import Iterable
from heapq import heappop, heappush

from bot.navigation.radar import Coordinate


def _heuristic(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _neighbors(node: tuple[int, int]) -> list[tuple[int, int]]:
    x, y = node
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]


def _a_star(
    start: tuple[int, int],
    goal: tuple[int, int],
    walkable: set[tuple[int, int]],
) -> list[tuple[int, int]]:
    frontier: list[tuple[int, tuple[int, int]]] = []
    heappush(frontier, (0, start))

    came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    g_score: dict[tuple[int, int], int] = {start: 0}

    while frontier:
        _, current = heappop(frontier)
        if current == goal:
            break

        for nxt in _neighbors(current):
            if nxt not in walkable:
                continue

            new_cost = g_score[current] + 1
            if nxt not in g_score or new_cost < g_score[nxt]:
                g_score[nxt] = new_cost
                priority = new_cost + _heuristic(nxt, goal)
                heappush(frontier, (priority, nxt))
                came_from[nxt] = current

    if goal not in came_from:
        return []

    path: list[tuple[int, int]] = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from[current]  # type: ignore[assignment]
    path.reverse()
    return path


def generateFloorWalkpoints(
    current: Coordinate,
    goal: Coordinate,
    non_walkable_coordinates: Iterable[Coordinate],
    radius: int = 60,
) -> list[Coordinate]:
    if current[2] != goal[2]:
        raise ValueError("Mudança de floor deve ser tratada por task específica (escada/rope/shovel).")

    z = current[2]
    blocked = {(x, y) for x, y, floor in non_walkable_coordinates if floor == z}

    min_x, max_x = min(current[0], goal[0]) - radius, max(current[0], goal[0]) + radius
    min_y, max_y = min(current[1], goal[1]) - radius, max(current[1], goal[1]) + radius

    walkable = {
        (x, y)
        for x in range(min_x, max_x + 1)
        for y in range(min_y, max_y + 1)
        if (x, y) not in blocked
    }

    path_2d = _a_star((current[0], current[1]), (goal[0], goal[1]), walkable)
    return [(x, y, z) for x, y in path_2d]
