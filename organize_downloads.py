import shutil
import logging
from pathlib import Path
import argparse
import sys

# Define file type categories
file_types = {
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv"],
    "Audio": [".mp3", ".wav", ".m4a", ".aac", ".ogg"],
    "Archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
    "Scripts": [".py", ".js", ".sh", ".rb", ".pl"],
    "Applications": [".dmg", ".pkg", ".app"],
    "Others": []  # Anything that doesn't match above
}

# Extensions that indicate in-progress downloads
IN_PROGRESS_EXTS = [".part", ".crdownload", ".tmp"]

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def is_hidden_or_system(file_path: Path) -> bool:
    """Return True if the file is hidden or a common system file."""
    return file_path.name.startswith('.') or file_path.name in {'.DS_Store', 'Thumbs.db'}

def is_in_progress(file_path: Path) -> bool:
    """Return True if the file looks like an in-progress download."""
    return any(file_path.name.endswith(ext) for ext in IN_PROGRESS_EXTS)

def get_unique_destination(dest_folder: Path, file_name: str) -> Path:
    """Return a unique file path in dest_folder for file_name to avoid overwriting."""
    dest_file = dest_folder / file_name
    if not dest_file.exists():
        return dest_file
    stem = dest_file.stem
    suffix = dest_file.suffix
    i = 1
    while True:
        new_name = f"{stem} ({i}){suffix}"
        candidate = dest_folder / new_name
        if not candidate.exists():
            return candidate
        i += 1

def move_file(file_path: Path, downloads_path: Path):
    if file_path.is_dir():
        return  # skip directories
    if is_hidden_or_system(file_path):
        return  # skip hidden/system files
    if is_in_progress(file_path):
        return  # skip in-progress downloads

    file_ext = file_path.suffix.lower()
    destination_folder = "Others"
    for folder, extensions in file_types.items():
        if file_ext in extensions:
            destination_folder = folder
            break

    destination_path = downloads_path / destination_folder
    destination_path.mkdir(exist_ok=True)
    dest_file = get_unique_destination(destination_path, file_path.name)

    try:
        shutil.move(str(file_path), str(dest_file))
        logging.info(f"Moved: {file_path.name}  {destination_folder}")
    except Exception as e:
        logging.error(f"Failed to move {file_path.name}: {e}")

def organize_downloads(downloads_path: Path):
    for file in downloads_path.iterdir():
        move_file(file, downloads_path)

def main():
    parser = argparse.ArgumentParser(description="Organize your Downloads folder by file type.")
    parser.add_argument(
        '-d', '--directory',
        type=str,
        default=str(Path.home() / "Downloads"),
        help="Directory to organize (default: ~/Downloads)"
    )
    args = parser.parse_args()
    downloads_path = Path(args.directory).expanduser().resolve()
    if not downloads_path.exists() or not downloads_path.is_dir():
        logging.error(f"Provided path {downloads_path} does not exist or is not a directory.")
        sys.exit(1)
    organize_downloads(downloads_path)

if __name__ == "__main__":
    main()
