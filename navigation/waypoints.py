from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class Waypoint:
    id: str
    x: int
    y: int
    action: Optional[str] = None


def load_waypoints(path: str) -> list[Waypoint]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    waypoints = [Waypoint(**item) for item in data["waypoints"]]
    if not waypoints:
        raise ValueError("Arquivo de waypoints sem pontos")
    return waypoints
