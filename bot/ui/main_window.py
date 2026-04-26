from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from bot.action.keyboard_controller import KeyboardController
from bot.core.models import NavigationConfig, ScreenRegion
from bot.navigation.waypoint_navigator import WaypointNavigator
from bot.perception.minimap_detector import MinimapDetector
from bot.ui.region_selector import RegionSelector


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("OTServer Navigator (autorizado)")

        self._game_region: ScreenRegion | None = None
        self._minimap_region: ScreenRegion | None = None
        self._selector: RegionSelector | None = None
        self._navigator: WaypointNavigator | None = None

        self._timer = QTimer(self)
        self._timer.setInterval(150)
        self._timer.timeout.connect(self._on_tick)

        root = QWidget()
        layout = QVBoxLayout(root)
        form = QFormLayout()

        self._game_label = QLabel("Não selecionado")
        self._map_label = QLabel("Não selecionado")
        form.addRow("Tela do jogo:", self._game_label)
        form.addRow("Minimapa:", self._map_label)
        layout.addLayout(form)

        row = QHBoxLayout()
        btn_game = QPushButton("Selecionar tela do jogo")
        btn_game.clicked.connect(lambda: self._open_selector("game"))
        btn_map = QPushButton("Selecionar minimapa")
        btn_map.clicked.connect(lambda: self._open_selector("map"))
        row.addWidget(btn_game)
        row.addWidget(btn_map)
        layout.addLayout(row)

        row2 = QHBoxLayout()
        self._start_btn = QPushButton("Iniciar navegação")
        self._start_btn.clicked.connect(self._toggle_navigation)
        self._status = QLabel("Parado")
        row2.addWidget(self._start_btn)
        row2.addWidget(self._status)
        layout.addLayout(row2)

        layout.addWidget(QLabel("Use apenas em OTServer com automação permitida."))
        self.setCentralWidget(root)

    def _open_selector(self, target: str) -> None:
        self.hide()
        selector = RegionSelector()

        def on_selected(rect):
            region = ScreenRegion(rect.left(), rect.top(), rect.width(), rect.height())
            if target == "game":
                self._game_region = region
                self._game_label.setText(self._fmt_region(region))
            else:
                self._minimap_region = region
                self._map_label.setText(self._fmt_region(region))

            self.show()
            self.activateWindow()

        selector.region_selected.connect(on_selected)
        selector.show()
        self._selector = selector

    def _toggle_navigation(self) -> None:
        if self._timer.isActive():
            self._timer.stop()
            self._navigator = None
            self._start_btn.setText("Iniciar navegação")
            self._status.setText("Parado")
            return

        if self._game_region is None or self._minimap_region is None:
            self._status.setText("Selecione as duas regiões primeiro")
            return

        config = NavigationConfig(
            game_region=self._game_region,
            minimap_region=self._minimap_region,
        )
        self._navigator = WaypointNavigator(
            config=config,
            detector=MinimapDetector(config),
            keyboard=KeyboardController(),
        )
        self._timer.start()
        self._start_btn.setText("Parar")
        self._status.setText("Rodando")

    def _on_tick(self) -> None:
        if not self._navigator:
            return
        decision = self._navigator.tick()
        if decision.key:
            self._status.setText(
                f"Movendo {decision.key.upper()} (dx={decision.delta_x}, dy={decision.delta_y})"
            )
        else:
            self._status.setText("Aguardando waypoint/jogador")

    @staticmethod
    def _fmt_region(region: ScreenRegion) -> str:
        return f"x={region.left}, y={region.top}, w={region.width}, h={region.height}"


def run() -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.resize(560, 220)
    window.show()
    app.exec()
