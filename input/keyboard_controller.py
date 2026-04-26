from __future__ import annotations

import platform
import time
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(slots=True)
class KeyMapping:
    up: str = "w"
    down: str = "s"
    left: str = "a"
    right: str = "d"


class KeyboardController:
    """Camada de teclado com backend injetável e fallback seguro para ambientes headless."""

    def __init__(self, mapping: Optional[KeyMapping] = None, sender: Optional[Callable[[str], None]] = None) -> None:
        self.mapping = mapping or KeyMapping()
        self._sender = sender or self._default_sender

    def tap(self, key_name: str) -> None:
        self._sender(self._resolve_key(key_name))

    def move_step(self, horizontal: Optional[str], vertical: Optional[str]) -> None:
        if horizontal:
            self.tap(horizontal)
        if vertical:
            self.tap(vertical)

    def _resolve_key(self, name: str) -> str:
        return getattr(self.mapping, name)

    @staticmethod
    def _default_sender(key: str) -> None:
        # MVP: evita dependência de GUI no Linux headless durante testes.
        # Em Windows, este método pode ser trocado por implementação de SendInput.
        if platform.system() == "Windows":
            # Placeholder operacional mínimo: pequeno delay para não saturar loop.
            time.sleep(0.005)
            return
        time.sleep(0.002)
