from __future__ import annotations

import argparse
from pathlib import Path

from bot.navigation.map_repository import install_maps_from_folder, install_maps_from_github_zip
from bot.navigation.pathfinding import generateFloorWalkpoints


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bot-farm", description="Ferramentas utilitárias do bot OTServer autorizado")
    subparsers = parser.add_subparsers(dest="command", required=True)

    path_parser = subparsers.add_parser("pathfinding", help="Gera caminho A* entre duas coordenadas no mesmo floor")
    path_parser.add_argument("--current", nargs=3, type=int, required=True, metavar=("X", "Y", "Z"))
    path_parser.add_argument("--goal", nargs=3, type=int, required=True, metavar=("X", "Y", "Z"))
    path_parser.add_argument(
        "--blocked",
        nargs=3,
        type=int,
        action="append",
        default=[],
        metavar=("X", "Y", "Z"),
        help="Pode ser repetido para múltiplos tiles não andáveis.",
    )

    maps_parser = subparsers.add_parser("install-maps", help="Instala mapas do radar")
    source_group = maps_parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--source-folder", type=Path, help="Pasta local com imagens de mapa")
    source_group.add_argument("--github-zip", type=str, help="URL de zip do GitHub")
    maps_parser.add_argument("--target-folder", type=Path, default=Path("bot/assets/maps"))

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "pathfinding":
        current = tuple(args.current)
        goal = tuple(args.goal)
        blocked = [tuple(tile) for tile in args.blocked]
        path = generateFloorWalkpoints(current, goal, blocked)
        if not path:
            print("Nenhum caminho encontrado")
            return 1

        print(f"Waypoints: {len(path)}")
        for waypoint in path:
            print(waypoint)
        return 0

    if args.command == "install-maps":
        if args.source_folder:
            destination = install_maps_from_folder(args.source_folder, args.target_folder)
            print(f"Mapas instalados de pasta local em: {destination}")
            return 0

        destination = install_maps_from_github_zip(args.github_zip, args.target_folder)
        print(f"Mapas instalados de zip GitHub em: {destination}")
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
