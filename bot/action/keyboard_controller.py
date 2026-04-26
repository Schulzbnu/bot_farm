from __future__ import annotations

import time

from pynput.keyboard import Controller, KeyCode


class KeyboardController:
    """Camada única de envio de teclas para manter simplicidade."""

    def __init__(self) -> None:
        self._kb = Controller()

    def tap(self, key: str, hold_seconds: float) -> None:
        code = KeyCode.from_char(key)
        self._kb.press(code)
        time.sleep(hold_seconds)
        self._kb.release(code)
