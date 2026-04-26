from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.bot_engine import BotEngine
from input.keyboard_controller import KeyboardController
from navigation.path_executor import PathExecutor
from navigation.waypoints import load_waypoints
from vision.player_detection import PlayerDetector
from vision.screen_capture import ScreenCapture


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("OTServer Bot - Waypoints")
        self.capture = ScreenCapture()
        self.waypoint_file: Optional[str] = None
        self.bot: Optional[BotEngine] = None
        self._build_ui()
        self._load_monitors()

    def _build_ui(self) -> None:
        self.monitor_list = QListWidget()
        self.preview_label = QLabel("Preview desativado (MVP)")
        self.waypoint_label = QLabel("Waypoints: não carregado")

        load_btn = QPushButton("Carregar waypoints")
        load_btn.clicked.connect(self._load_waypoints_file)

        self.start_btn = QPushButton("Iniciar")
        self.start_btn.clicked.connect(self._start_bot)
        stop_btn = QPushButton("Parar")
        stop_btn.clicked.connect(self._stop_bot)

        root = QWidget()
        col = QVBoxLayout(root)
        col.addWidget(QLabel("Monitores disponíveis"))
        col.addWidget(self.monitor_list)
        col.addWidget(self.preview_label)
        col.addWidget(self.waypoint_label)

        row = QHBoxLayout()
        row.addWidget(load_btn)
        row.addWidget(self.start_btn)
        row.addWidget(stop_btn)
        col.addLayout(row)
        self.setCentralWidget(root)

    def _load_monitors(self) -> None:
        for i, monitor in enumerate(self.capture.list_monitors(), start=1):
            text = f"Monitor {i}: {monitor['width']}x{monitor['height']} ({monitor['left']},{monitor['top']})"
            self.monitor_list.addItem(text)
        self.monitor_list.setCurrentRow(0)

    def _load_waypoints_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Selecione waypoints", str(Path.cwd()), "JSON (*.json)")
        if path:
            self.waypoint_file = path
            self.waypoint_label.setText(f"Waypoints: {Path(path).name}")

    def _start_bot(self) -> None:
        if not self.waypoint_file:
            self.waypoint_label.setText("Waypoints: selecione um arquivo antes de iniciar")
            return

        monitor_idx = self.monitor_list.currentRow() + 1
        region = self.capture.monitor_region(monitor_idx)
        waypoints = load_waypoints(self.waypoint_file)
        detector = PlayerDetector(template_path="data/player_template.png")
        executor = PathExecutor(waypoints)
        keyboard = KeyboardController()

        self.bot = BotEngine(self.capture, detector, executor, keyboard, region)
        self.bot.start()
        self.start_btn.setEnabled(False)

    def _stop_bot(self) -> None:
        if self.bot:
            self.bot.stop()
            self.start_btn.setEnabled(True)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._stop_bot()
        self.capture.close()
        event.accept()
