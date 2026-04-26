from __future__ import annotations

from pathlib import Path
from urllib.request import urlretrieve
import zipfile

DEFAULT_MAPS_DIR = Path("bot/assets/maps")


def ensure_maps_dir(path: Path = DEFAULT_MAPS_DIR) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def install_maps_from_folder(source_folder: Path, target_folder: Path = DEFAULT_MAPS_DIR) -> Path:
    target_folder = ensure_maps_dir(target_folder)
    for item in source_folder.glob("**/*"):
        if not item.is_file():
            continue
        relative = item.relative_to(source_folder)
        destination = target_folder / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(item.read_bytes())
    return target_folder


def install_maps_from_github_zip(zip_url: str, target_folder: Path = DEFAULT_MAPS_DIR) -> Path:
    target_folder = ensure_maps_dir(target_folder)
    zip_path = target_folder / "maps_repo.zip"
    temp_extract = target_folder / "_tmp_extract"

    urlretrieve(zip_url, zip_path)
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(temp_extract)

    extracted_roots = [p for p in temp_extract.iterdir() if p.is_dir()]
    root = extracted_roots[0] if extracted_roots else temp_extract

    for item in root.glob("**/*"):
        if not item.is_file():
            continue
        relative = item.relative_to(root)
        destination = target_folder / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(item.read_bytes())

    zip_path.unlink(missing_ok=True)
    for child in sorted(temp_extract.glob("**/*"), reverse=True):
        if child.is_file():
            child.unlink(missing_ok=True)
        elif child.is_dir():
            child.rmdir()
    temp_extract.rmdir()

    return target_folder
