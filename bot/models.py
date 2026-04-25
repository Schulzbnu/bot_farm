from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int
    z: int = 0


WaypointList = List[Coordinate]


@dataclass
class ScreenRegion:
    name: str
    x: int
    y: int
    width: int
    height: int


@dataclass
class ProfileConfig:
    """Configuração de regiões de tela necessárias para o bot."""

    regions: Dict[str, ScreenRegion] = field(default_factory=dict)

    def upsert_region(self, region: ScreenRegion) -> None:
        self.regions[region.name] = region

    def list_regions(self) -> List[ScreenRegion]:
        return list(self.regions.values())

    def get_region(self, name: str) -> ScreenRegion | None:
        return self.regions.get(name)
