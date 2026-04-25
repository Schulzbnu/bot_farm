from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from bot.models import Coordinate, ProfileConfig, ScreenRegion
from bot.movement import MovementController, MovementState, parse_waypoint_lines
from bot.perception import PerceptionSettings, PerceptionState, ScreenPerceptionService


class RegionDialog(tk.Toplevel):
    def __init__(self, master: tk.Misc, on_save) -> None:
        super().__init__(master)
        self.title("Selecionar região")
        self.resizable(False, False)
        self.on_save = on_save

        self.var_name = tk.StringVar(value="minimap")
        self.var_x = tk.StringVar(value="0")
        self.var_y = tk.StringVar(value="0")
        self.var_w = tk.StringVar(value="200")
        self.var_h = tk.StringVar(value="200")

        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self, padding=12)
        frame.grid(sticky="nsew")

        entries = [
            ("Nome", self.var_name),
            ("X", self.var_x),
            ("Y", self.var_y),
            ("Largura", self.var_w),
            ("Altura", self.var_h),
        ]

        for row, (label, var) in enumerate(entries):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=4)
            ttk.Entry(frame, textvariable=var, width=24).grid(row=row, column=1, sticky="ew", pady=4)

        ttk.Button(frame, text="Salvar", command=self._save).grid(
            row=len(entries),
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(12, 0),
        )

    def _save(self) -> None:
        try:
            region = ScreenRegion(
                name=self.var_name.get().strip(),
                x=int(self.var_x.get()),
                y=int(self.var_y.get()),
                width=int(self.var_w.get()),
                height=int(self.var_h.get()),
            )
        except ValueError:
            messagebox.showerror("Valor inválido", "X, Y, largura e altura devem ser números inteiros.")
            return

        if not region.name:
            messagebox.showerror("Nome obrigatório", "Informe um nome para a região.")
            return

        self.on_save(region)
        self.destroy()


class BotApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Bot OTServer - Cavehunting MVP")
        self.geometry("980x790")

        self.profile = ProfileConfig()
        self.controller = MovementController()
        self.controller.on_state_update(self._on_movement_state_update)

        self.perception = ScreenPerceptionService(self.profile, self.controller)
        self.perception.on_state_update(self._on_perception_state_update)

        self.var_status = tk.StringVar(value="Parado")
        self.var_position = tk.StringVar(value="(0, 0, 0)")
        self.var_current_wp = tk.StringVar(value="-")
        self.var_nearest_wp = tk.StringVar(value="-")

        self.var_pos_x = tk.StringVar(value="0")
        self.var_pos_y = tk.StringVar(value="0")
        self.var_pos_z = tk.StringVar(value="7")

        self.var_perception_status = tk.StringVar(value="Percepção parada")
        self.var_marker_pixel = tk.StringVar(value="-")

        self.var_region_name = tk.StringVar(value="minimap")
        self.var_origin_x = tk.StringVar(value="100")
        self.var_origin_y = tk.StringVar(value="100")
        self.var_origin_z = tk.StringVar(value="7")
        self.var_tile_size = tk.StringVar(value="8.0")
        self.var_fps = tk.StringVar(value="4.0")

        self.var_h_min = tk.StringVar(value="0")
        self.var_s_min = tk.StringVar(value="0")
        self.var_v_min = tk.StringVar(value="220")
        self.var_h_max = tk.StringVar(value="179")
        self.var_s_max = tk.StringVar(value="45")
        self.var_v_max = tk.StringVar(value="255")

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build_layout()

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        self._build_waypoint_section(root)
        self._build_position_section(root)
        self._build_control_section(root)
        self._build_regions_section(root)
        self._build_perception_section(root)
        self._build_status_section(root)

    def _build_waypoint_section(self, parent: ttk.Frame) -> None:
        card = ttk.LabelFrame(parent, text="Waypoints (x,y,z por linha)", padding=10)
        card.pack(fill="x", pady=(0, 8))

        self.waypoints_text = tk.Text(card, height=8)
        self.waypoints_text.pack(fill="x")
        self.waypoints_text.insert(
            "1.0",
            "100,100,7\n"
            "104,100,7\n"
            "104,104,7\n"
            "100,104,7\n",
        )

        ttk.Button(card, text="Carregar waypoints", command=self._load_waypoints).pack(fill="x", pady=(8, 0))

    def _build_position_section(self, parent: ttk.Frame) -> None:
        card = ttk.LabelFrame(parent, text="Posição atual (manual)", padding=10)
        card.pack(fill="x", pady=(0, 8))

        row = ttk.Frame(card)
        row.pack(fill="x")

        ttk.Label(row, text="X").pack(side="left")
        ttk.Entry(row, width=8, textvariable=self.var_pos_x).pack(side="left", padx=(4, 12))

        ttk.Label(row, text="Y").pack(side="left")
        ttk.Entry(row, width=8, textvariable=self.var_pos_y).pack(side="left", padx=(4, 12))

        ttk.Label(row, text="Z").pack(side="left")
        ttk.Entry(row, width=8, textvariable=self.var_pos_z).pack(side="left", padx=(4, 12))

        ttk.Button(row, text="Aplicar posição", command=self._apply_position).pack(side="left")

    def _build_control_section(self, parent: ttk.Frame) -> None:
        card = ttk.LabelFrame(parent, text="Controle de movimentação", padding=10)
        card.pack(fill="x", pady=(0, 8))

        row = ttk.Frame(card)
        row.pack(fill="x")

        ttk.Button(row, text="Ativar movimentação", command=self._start_movement).pack(side="left", padx=(0, 8))
        ttk.Button(row, text="Parar movimentação", command=self._stop_movement).pack(side="left", padx=(0, 8))
        ttk.Button(row, text="Descobrir waypoint atual", command=self._discover_current_waypoint).pack(side="left")

    def _build_regions_section(self, parent: ttk.Frame) -> None:
        card = ttk.LabelFrame(parent, text="Regiões necessárias (perception)", padding=10)
        card.pack(fill="both", expand=True, pady=(0, 8))

        ttk.Button(card, text="Selecionar localização de região", command=self._open_region_dialog).pack(
            fill="x",
            pady=(0, 8),
        )

        self.regions_table = ttk.Treeview(card, columns=("name", "x", "y", "w", "h"), show="headings", height=5)
        self.regions_table.heading("name", text="Nome")
        self.regions_table.heading("x", text="X")
        self.regions_table.heading("y", text="Y")
        self.regions_table.heading("w", text="Largura")
        self.regions_table.heading("h", text="Altura")

        self.regions_table.column("name", width=180)
        self.regions_table.column("x", width=80)
        self.regions_table.column("y", width=80)
        self.regions_table.column("w", width=80)
        self.regions_table.column("h", width=80)
        self.regions_table.pack(fill="both", expand=True)

    def _build_perception_section(self, parent: ttk.Frame) -> None:
        card = ttk.LabelFrame(parent, text="Percepção real de tela (minimap)", padding=10)
        card.pack(fill="x", pady=(0, 8))

        row1 = ttk.Frame(card)
        row1.pack(fill="x", pady=(0, 6))
        self._labeled_entry(row1, "Região", self.var_region_name)
        self._labeled_entry(row1, "Origem X", self.var_origin_x)
        self._labeled_entry(row1, "Origem Y", self.var_origin_y)
        self._labeled_entry(row1, "Origem Z", self.var_origin_z)
        self._labeled_entry(row1, "Tile px", self.var_tile_size)
        self._labeled_entry(row1, "FPS", self.var_fps)

        row2 = ttk.Frame(card)
        row2.pack(fill="x", pady=(0, 6))
        self._labeled_entry(row2, "H min", self.var_h_min)
        self._labeled_entry(row2, "S min", self.var_s_min)
        self._labeled_entry(row2, "V min", self.var_v_min)
        self._labeled_entry(row2, "H max", self.var_h_max)
        self._labeled_entry(row2, "S max", self.var_s_max)
        self._labeled_entry(row2, "V max", self.var_v_max)

        row3 = ttk.Frame(card)
        row3.pack(fill="x")
        ttk.Button(row3, text="Ativar percepção", command=self._start_perception).pack(side="left", padx=(0, 8))
        ttk.Button(row3, text="Parar percepção", command=self._stop_perception).pack(side="left")

        if not ScreenPerceptionService.dependencies_available():
            ttk.Label(
                card,
                text="Dependências ausentes: instale mss, numpy e opencv-python para ativar.",
                foreground="#b26a00",
            ).pack(anchor="w", pady=(8, 0))

    def _build_status_section(self, parent: ttk.Frame) -> None:
        card = ttk.LabelFrame(parent, text="Status", padding=10)
        card.pack(fill="x")

        ttk.Label(card, text="Movimentação: ").grid(row=0, column=0, sticky="w")
        ttk.Label(card, textvariable=self.var_status).grid(row=0, column=1, sticky="w")

        ttk.Label(card, text="Posição atual: ").grid(row=1, column=0, sticky="w")
        ttk.Label(card, textvariable=self.var_position).grid(row=1, column=1, sticky="w")

        ttk.Label(card, text="Waypoint alvo: ").grid(row=2, column=0, sticky="w")
        ttk.Label(card, textvariable=self.var_current_wp).grid(row=2, column=1, sticky="w")

        ttk.Label(card, text="Waypoint mais próximo: ").grid(row=3, column=0, sticky="w")
        ttk.Label(card, textvariable=self.var_nearest_wp).grid(row=3, column=1, sticky="w")

        ttk.Label(card, text="Percepção: ").grid(row=4, column=0, sticky="w")
        ttk.Label(card, textvariable=self.var_perception_status).grid(row=4, column=1, sticky="w")

        ttk.Label(card, text="Marcador (px): ").grid(row=5, column=0, sticky="w")
        ttk.Label(card, textvariable=self.var_marker_pixel).grid(row=5, column=1, sticky="w")

    @staticmethod
    def _labeled_entry(parent: ttk.Frame, label: str, variable: tk.StringVar, width: int = 7) -> None:
        ttk.Label(parent, text=label).pack(side="left")
        ttk.Entry(parent, textvariable=variable, width=width).pack(side="left", padx=(4, 8))

    def _load_waypoints(self) -> None:
        try:
            waypoints = parse_waypoint_lines(self.waypoints_text.get("1.0", "end"))
            self.controller.set_waypoints(waypoints)
            messagebox.showinfo("Waypoints", f"{len(waypoints)} waypoints carregados.")
            self._refresh_waypoint_labels()
        except ValueError as exc:
            messagebox.showerror("Erro ao carregar", str(exc))

    def _apply_position(self) -> None:
        try:
            coordinate = Coordinate(int(self.var_pos_x.get()), int(self.var_pos_y.get()), int(self.var_pos_z.get()))
            self.controller.set_current_position(coordinate)
            self._refresh_waypoint_labels()
        except ValueError:
            messagebox.showerror("Valor inválido", "X, Y e Z precisam ser inteiros.")

    def _start_movement(self) -> None:
        try:
            self.controller.start()
        except ValueError as exc:
            messagebox.showerror("Não foi possível iniciar", str(exc))

    def _stop_movement(self) -> None:
        self.controller.stop()

    def _discover_current_waypoint(self) -> None:
        nearest = self.controller.nearest_waypoint()
        if nearest is None:
            messagebox.showwarning("Sem waypoints", "Carregue waypoints antes de descobrir o atual.")
            return

        self.var_nearest_wp.set(self._format_coord(nearest))
        messagebox.showinfo("Waypoint atual", f"Waypoint mais próximo: {self._format_coord(nearest)}")

    def _start_perception(self) -> None:
        try:
            settings = self._parse_perception_settings_from_ui()
            self.perception.configure(settings)
            self.perception.start()
        except (ValueError, RuntimeError) as exc:
            messagebox.showerror("Percepção", str(exc))

    def _stop_perception(self) -> None:
        self.perception.stop()

    def _parse_perception_settings_from_ui(self) -> PerceptionSettings:
        return PerceptionSettings(
            region_name=self.var_region_name.get().strip(),
            origin_x=int(self.var_origin_x.get()),
            origin_y=int(self.var_origin_y.get()),
            origin_z=int(self.var_origin_z.get()),
            tile_size_px=float(self.var_tile_size.get()),
            fps=float(self.var_fps.get()),
            marker_h_min=int(self.var_h_min.get()),
            marker_s_min=int(self.var_s_min.get()),
            marker_v_min=int(self.var_v_min.get()),
            marker_h_max=int(self.var_h_max.get()),
            marker_s_max=int(self.var_s_max.get()),
            marker_v_max=int(self.var_v_max.get()),
        )

    def _open_region_dialog(self) -> None:
        dialog = RegionDialog(self, self._save_region)
        dialog.transient(self)
        dialog.grab_set()

    def _save_region(self, region: ScreenRegion) -> None:
        self.profile.upsert_region(region)
        self._refresh_regions_table()

    def _refresh_regions_table(self) -> None:
        for row_id in self.regions_table.get_children():
            self.regions_table.delete(row_id)

        for region in self.profile.list_regions():
            self.regions_table.insert(
                "",
                "end",
                values=(region.name, region.x, region.y, region.width, region.height),
            )

    def _on_movement_state_update(self, state: MovementState) -> None:
        self.after(0, lambda: self._apply_movement_state_snapshot(state))

    def _on_perception_state_update(self, state: PerceptionState) -> None:
        self.after(0, lambda: self._apply_perception_state_snapshot(state))

    def _apply_movement_state_snapshot(self, state: MovementState) -> None:
        self.var_status.set("Em execução" if state.is_running else "Parado")
        self.var_position.set(self._format_coord(state.current_position))
        self._refresh_waypoint_labels()

    def _apply_perception_state_snapshot(self, state: PerceptionState) -> None:
        self.var_perception_status.set(state.message)
        if state.last_marker_px is None:
            self.var_marker_pixel.set("-")
        else:
            self.var_marker_pixel.set(f"({state.last_marker_px[0]}, {state.last_marker_px[1]})")

    def _refresh_waypoint_labels(self) -> None:
        target = self.controller.current_target_waypoint()
        nearest = self.controller.nearest_waypoint()

        self.var_current_wp.set(self._format_coord(target) if target else "-")
        self.var_nearest_wp.set(self._format_coord(nearest) if nearest else "-")

    def _on_close(self) -> None:
        self.perception.stop()
        self.controller.stop()
        self.destroy()

    @staticmethod
    def _format_coord(coord: Coordinate | None) -> str:
        if coord is None:
            return "-"
        return f"({coord.x}, {coord.y}, {coord.z})"


def run_app() -> None:
    app = BotApp()
    app.mainloop()
