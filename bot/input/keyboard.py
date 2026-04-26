from __future__ import annotations

from dataclasses import dataclass
from time import sleep


@dataclass(slots=True)
class KeyboardController:
    """Camada de input desacoplada para permitir mock em testes."""

    key_hold_ms: int = 45

    def press(self, key: str) -> None:
        # Trocar por implementação real (pynput/pyautogui) na integração.
        return

    def keyDown(self, key: str) -> None:
        return

    def releaseKeys(self) -> None:
        return

    def tap(self, key: str, hold_multiplier: float = 1.0) -> None:
        self.keyDown(key)
        sleep((self.key_hold_ms * hold_multiplier) / 1000)
        self.releaseKeys()
        self.press(key)
