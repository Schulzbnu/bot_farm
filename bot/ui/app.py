from __future__ import annotations

import json
import tkinter as tk
from dataclasses import asdict
from tkinter import filedialog, messagebox

from bot.core.movement import MovementEngine, Waypoint
from bot.core.pathfinding import Coordinate, MapGrid

CELL = 28


class MovementMVPApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MVP - Movimentação por Mapa")

        self.grid = MapGrid(width=20, height=14, floor=0, blocked={(6, 6), (7, 6), (8, 6)})
        self.waypoints = [
            Waypoint("wp1", Coordinate(3, 3, 0)),
            Waypoint("wp2", Coordinate(15, 4, 0)),
            Waypoint("wp3", Coordinate(12, 10, 0)),
        ]
        self.start = Coordinate(1, 1, 0)
        self.engine = MovementEngine(self.grid, self.waypoints, self.start)

        self.running = False
        self.tick_ms = tk.IntVar(value=180)
        self.map_size = tk.StringVar(value=f"{self.grid.width}x{self.grid.height}")
        self.start_var = tk.StringVar(value="1,1,0")
        self.blocked_var = tk.StringVar(value="6,6;7,6;8,6")
        self.wp_var = tk.StringVar(value="3,3,0;15,4,0;12,10,0")

        self._build()
        self._draw()

    def _build(self) -> None:
        left = tk.Frame(self.root)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)

        self.canvas = tk.Canvas(self.root, width=self.grid.width * CELL, height=self.grid.height * CELL, bg="white")
        self.canvas.pack(side=tk.RIGHT, padx=10, pady=10)

        self._field(left, "Mapa (LxA)", self.map_size)
        self._field(left, "Start (x,y,z)", self.start_var)
        self._field(left, "Bloqueios (x,y;...)", self.blocked_var)
        self._field(left, "Waypoints (x,y,z;...)", self.wp_var)
        self._field(left, "Tick ms", self.tick_ms)

        tk.Button(left, text="Aplicar parâmetros", command=self.apply_params).pack(fill=tk.X, pady=(8, 2))
        tk.Button(left, text="Iniciar", command=self.start_run).pack(fill=tk.X, pady=2)
        tk.Button(left, text="Pausar", command=self.pause_run).pack(fill=tk.X, pady=2)
        tk.Button(left, text="Step", command=self.step_once).pack(fill=tk.X, pady=2)
        tk.Button(left, text="Reset", command=self.reset).pack(fill=tk.X, pady=2)
        tk.Button(left, text="Salvar perfil", command=self.save_profile).pack(fill=tk.X, pady=(14, 2))
        tk.Button(left, text="Carregar perfil", command=self.load_profile).pack(fill=tk.X, pady=2)

        self.status = tk.Label(left, text="Pronto", anchor="w", justify="left")
        self.status.pack(fill=tk.X, pady=(10, 0))

    @staticmethod
    def _field(parent: tk.Widget, label: str, var: tk.Variable) -> None:
        tk.Label(parent, text=label).pack(anchor="w")
        tk.Entry(parent, textvariable=var, width=36).pack(fill=tk.X, pady=(0, 6))

    def _parse_xyz_list(self, raw: str) -> list[Coordinate]:
        coords = []
        for chunk in [x.strip() for x in raw.split(";") if x.strip()]:
            parts = [p.strip() for p in chunk.split(",")]
            if len(parts) != 3:
                raise ValueError(f"Coordenada inválida: {chunk}")
            x, y, z = map(int, parts)
            coords.append(Coordinate(x, y, z))
        return coords

    def _parse_xy_set(self, raw: str) -> set[tuple[int, int]]:
        pts: set[tuple[int, int]] = set()
        for chunk in [x.strip() for x in raw.split(";") if x.strip()]:
            parts = [p.strip() for p in chunk.split(",")]
            if len(parts) != 2:
                raise ValueError(f"Bloqueio inválido: {chunk}")
            x, y = map(int, parts)
            pts.add((x, y))
        return pts

    def apply_params(self) -> None:
        try:
            width, height = [int(v.strip()) for v in self.map_size.get().lower().split("x")]
            start = self._parse_xyz_list(self.start_var.get())
            waypoints = self._parse_xyz_list(self.wp_var.get())
            blocked = self._parse_xy_set(self.blocked_var.get())
            if len(start) != 1:
                raise ValueError("Start deve conter apenas 1 coordenada")

            self.grid = MapGrid(width=width, height=height, floor=start[0].z, blocked=blocked)
            self.start = start[0]
            self.waypoints = [Waypoint(f"wp{i+1}", c) for i, c in enumerate(waypoints)]
            self.engine = MovementEngine(self.grid, self.waypoints, self.start)
            self.canvas.config(width=self.grid.width * CELL, height=self.grid.height * CELL)
            self.running = False
            self._set_status("Parâmetros aplicados")
            self._draw()
        except Exception as exc:
            messagebox.showerror("Erro nos parâmetros", str(exc))

    def _set_status(self, msg: str) -> None:
        st = self.engine.state
        current_wp = st.current_waypoint_index + 1 if not st.finished else len(self.waypoints)
        self.status.config(
            text=(
                f"{msg}\n"
                f"Posição: ({st.position.x},{st.position.y},{st.position.z})\n"
                f"Waypoint atual: {current_wp}/{len(self.waypoints)}\n"
                f"Finalizado: {'sim' if st.finished else 'não'}"
            )
        )

    def _draw(self) -> None:
        self.canvas.delete("all")
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                color = "#f2f2f2" if (x, y) in self.grid.blocked else "white"
                self.canvas.create_rectangle(x * CELL, y * CELL, (x + 1) * CELL, (y + 1) * CELL, outline="#d0d0d0", fill=color)

        for i, wp in enumerate(self.waypoints, start=1):
            self._draw_tile(wp.coordinate.x, wp.coordinate.y, "#66ccff")
            self.canvas.create_text(wp.coordinate.x * CELL + CELL / 2, wp.coordinate.y * CELL + CELL / 2, text=str(i), fill="black")

        path = self.engine.state.current_segment_path
        if len(path) > 1:
            for p in path[1:]:
                self._draw_tile(p.x, p.y, "#c5f7c5")

        pos = self.engine.state.position
        self._draw_tile(pos.x, pos.y, "#2d7cff")
        self._set_status("Executando" if self.running else "Pronto")

    def _draw_tile(self, x: int, y: int, color: str) -> None:
        self.canvas.create_rectangle(
            x * CELL + 4,
            y * CELL + 4,
            (x + 1) * CELL - 4,
            (y + 1) * CELL - 4,
            fill=color,
            outline="",
        )

    def start_run(self) -> None:
        if self.running:
            return
        self.running = True
        self._tick()

    def pause_run(self) -> None:
        self.running = False
        self._draw()

    def step_once(self) -> None:
        self.engine.step()
        self._draw()

    def _tick(self) -> None:
        if not self.running:
            return
        self.engine.step()
        self._draw()
        if self.engine.state.finished:
            self.running = False
            return
        self.root.after(max(30, self.tick_ms.get()), self._tick)

    def reset(self) -> None:
        self.running = False
        self.engine = MovementEngine(self.grid, self.waypoints, self.start)
        self._draw()

    def save_profile(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        payload = {
            "map": {"width": self.grid.width, "height": self.grid.height, "floor": self.grid.floor},
            "start": asdict(self.start),
            "blocked": [{"x": x, "y": y} for (x, y) in sorted(self.grid.blocked)],
            "waypoints": [
                {
                    "label": wp.label,
                    "type": wp.type,
                    "ignore": wp.ignore,
                    "passinho": wp.passinho,
                    "coordinate": asdict(wp.coordinate),
                }
                for wp in self.waypoints
            ],
            "tick_ms": self.tick_ms.get(),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        self._set_status(f"Perfil salvo em {path}")

    def load_profile(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        mp = payload["map"]
        self.map_size.set(f"{mp['width']}x{mp['height']}")
        st = payload["start"]
        self.start_var.set(f"{st['x']},{st['y']},{st['z']}")
        self.blocked_var.set(";".join([f"{b['x']},{b['y']}" for b in payload.get("blocked", [])]))
        self.wp_var.set(";".join([
            f"{w['coordinate']['x']},{w['coordinate']['y']},{w['coordinate']['z']}" for w in payload["waypoints"]
        ]))
        self.tick_ms.set(payload.get("tick_ms", 180))
        self.apply_params()
        self._set_status(f"Perfil carregado: {path}")


def run() -> None:
    root = tk.Tk()
    MovementMVPApp(root)
    root.mainloop()
