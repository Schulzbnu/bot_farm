from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import hashlib

import cv2
import numpy as np

Coordinate = tuple[int, int, int]
Pixel = tuple[int, int]

RADAR_TOOLS_TEMPLATE = Path("bot/assets/maps/radar_tools.png")
FLOOR_SLICE_WIDTH = 12
COORDINATE_OFFSET: Pixel = (31744, 30976)


@dataclass(slots=True)
class MapReference:
    """Imagem de referência do radar para um floor específico."""

    floor: int
    origin_pixel: Pixel
    image: np.ndarray


@dataclass(slots=True)
class RadarContext:
    """Dependências para reconhecimento do radar."""

    radar_hash_index: dict[str, Coordinate]
    floor_templates: dict[int, np.ndarray]
    map_references: list[MapReference]
    tools_template: np.ndarray
    radar_size: tuple[int, int]


def load_image(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"Imagem não encontrada: {path}")
    return image


def locate(haystack: np.ndarray, needle: np.ndarray, confidence: float = 0.9) -> tuple[int, int] | None:
    """Retorna canto superior esquerdo do template se houver match."""

    result = cv2.matchTemplate(haystack, needle, cv2.TM_CCOEFF_NORMED)
    _, max_value, _, max_loc = cv2.minMaxLoc(result)
    if max_value < confidence:
        return None
    return max_loc


def getRadarToolsPosition(screenshot: np.ndarray, tools_template: np.ndarray, confidence: float = 0.88) -> tuple[int, int]:
    position = locate(screenshot, tools_template, confidence=confidence)
    if position is None:
        raise RuntimeError("Não foi possível localizar os tools do radar na screenshot.")
    return position


def getRadarImage(
    screenshot: np.ndarray,
    tools_position: tuple[int, int],
    radar_size: tuple[int, int],
    top_left_offset: tuple[int, int] = (-170, -5),
) -> np.ndarray:
    x = tools_position[0] + top_left_offset[0]
    y = tools_position[1] + top_left_offset[1]
    width, height = radar_size
    return screenshot[y : y + height, x : x + width]


def getCoordinateFromPixel(pixel: Pixel, floor: int) -> Coordinate:
    return (pixel[0] + COORDINATE_OFFSET[0], pixel[1] + COORDINATE_OFFSET[1], floor)


def getPixelFromCoordinate(coordinate: Coordinate) -> Pixel:
    return (coordinate[0] - COORDINATE_OFFSET[0], coordinate[1] - COORDINATE_OFFSET[1])


def _radar_hash(radar_image: np.ndarray) -> str:
    resized = cv2.resize(radar_image, (64, 64), interpolation=cv2.INTER_AREA)
    return hashlib.sha1(resized.tobytes()).hexdigest()


def _detect_floor_level(radar_image: np.ndarray, floor_templates: dict[int, np.ndarray]) -> int:
    floor_slice = radar_image[:, -FLOOR_SLICE_WIDTH:]
    best_floor = 7
    best_score = -1.0

    for floor, template in floor_templates.items():
        result = cv2.matchTemplate(floor_slice, template, cv2.TM_CCOEFF_NORMED)
        _, score, _, _ = cv2.minMaxLoc(result)
        if score > best_score:
            best_score = score
            best_floor = floor
    return best_floor


def _match_map_reference(radar_image: np.ndarray, floor: int, references: Iterable[MapReference]) -> Coordinate:
    for reference in references:
        if reference.floor != floor:
            continue
        hit = locate(reference.image, radar_image, confidence=0.82)
        if hit:
            px = reference.origin_pixel[0] + hit[0]
            py = reference.origin_pixel[1] + hit[1]
            return getCoordinateFromPixel((px, py), floor)

    raise RuntimeError(f"Sem match de mapa para floor {floor}.")


def getCoordinate(screenshot: np.ndarray, context: RadarContext) -> Coordinate:
    tools_position = getRadarToolsPosition(screenshot, context.tools_template)
    radar_image = getRadarImage(screenshot, tools_position, context.radar_size)

    radar_key = _radar_hash(radar_image)
    if radar_key in context.radar_hash_index:
        return context.radar_hash_index[radar_key]

    floor = _detect_floor_level(radar_image, context.floor_templates)
    return _match_map_reference(radar_image, floor, context.map_references)
