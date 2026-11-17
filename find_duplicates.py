import hashlib
import shutil
import logging
import argparse
import sys
from pathlib import Path
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Directories to skip during scanning
SKIP_DIRS = {
    '.git', '.svn', '.hg', '__pycache__', 'node_modules',
    '.Trash', 'Library', '.cache', '.npm', '.local',
    'Applications', '.vscode', '.idea',
}

# Default name for the duplicates folder
DUPLICATES_FOLDER = "Duplicates"

# Minimum file size to consider (skip empty files)
MIN_FILE_SIZE = 1


def is_hidden_or_system(file_path: Path) -> bool:
    """Return True if the file is hidden or a common system file."""
    return file_path.name.startswith('.') or file_path.name in {'.DS_Store', 'Thumbs.db'}


def should_skip_dir(dir_path: Path) -> bool:
    """Return True if this directory should be skipped."""
    return dir_path.name in SKIP_DIRS or dir_path.name.startswith('.')


def hash_file(file_path: Path, chunk_size: int = 8192) -> str:
    """Return the SHA-256 hash of a file's contents."""
    h = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
    except (OSError, PermissionError) as e:
        logging.debug(f"Cannot read {file_path}: {e}")
        return ""
    return h.hexdigest()


def quick_hash(file_path: Path, size: int = 1024) -> str:
    """Return a hash of just the first 1KB for fast pre-filtering."""
    h = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            h.update(f.read(size))
    except (OSError, PermissionError):
        return ""
    return h.hexdigest()


def collect_files(scan_dirs: list[Path]) -> list[Path]:
    """Recursively collect all regular files from the given directories."""
    files = []
    seen_dirs = set()

    for scan_dir in scan_dirs:
        scan_dir = scan_dir.resolve()
        if scan_dir in seen_dirs:
            continue

        for path in scan_dir.rglob('*'):
            if path.is_dir():
                continue
            if any(should_skip_dir(parent) for parent in path.relative_to(scan_dir).parents if parent != Path('.')):
                continue
            if is_hidden_or_system(path):
                continue
            try:
                if path.stat().st_size < MIN_FILE_SIZE:
                    continue
            except (OSError, PermissionError):
                continue
            files.append(path)

        seen_dirs.add(scan_dir)

    return files


def find_duplicates(files: list[Path]) -> list[list[Path]]:
    """Find duplicate files using a size -> quick hash -> full hash strategy."""
    logging.info(f"Scanning {len(files)} files...")

    # Step 1: Group by file size
    size_groups = defaultdict(list)
    for f in files:
        try:
            size_groups[f.stat().st_size].append(f)
        except (OSError, PermissionError):
            continue

    candidates = []
    for size, group in size_groups.items():
        if len(group) > 1:
            candidates.extend(group)

    logging.info(f"Found {len(candidates)} files with matching sizes, narrowing down...")

    # Step 2: Group by quick hash (first 1KB)
    quick_groups = defaultdict(list)
    for f in candidates:
        qh = quick_hash(f)
        if qh:
            quick_groups[(f.stat().st_size, qh)].append(f)

    narrowed = []
    for key, group in quick_groups.items():
        if len(group) > 1:
            narrowed.extend(group)

    logging.info(f"Narrowed to {len(narrowed)} files with matching quick hashes, computing full hashes...")

    # Step 3: Group by full hash
    full_groups = defaultdict(list)
    for f in narrowed:
        fh = hash_file(f)
        if fh:
            full_groups[fh].append(f)

    duplicates = []
    for file_hash, group in full_groups.items():
        if len(group) > 1:
            duplicates.append(sorted(group, key=lambda p: p.stat().st_mtime))

    return duplicates


def get_unique_destination(dest_folder: Path, file_name: str) -> Path:
    """Return a unique file path in dest_folder to avoid overwriting."""
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


def move_duplicates(duplicate_groups: list[list[Path]], duplicates_dir: Path, dry_run: bool = False):
    """Move duplicate files to the duplicates directory, keeping the oldest copy in place."""
    duplicates_dir.mkdir(exist_ok=True)
    moved_count = 0

    for group in duplicate_groups:
        # Keep the oldest file (first in sorted list), move the rest
        original = group[0]
        logging.info(f"\nOriginal (kept): {original}")

        for dup in group[1:]:
            dest = get_unique_destination(duplicates_dir, dup.name)
            if dry_run:
                logging.info(f"  Would move: {dup}")
            else:
                try:
                    shutil.move(str(dup), str(dest))
                    logging.info(f"  Moved: {dup} -> {dest.name}")
                    moved_count += 1
                except Exception as e:
                    logging.error(f"  Failed to move {dup}: {e}")

    return moved_count


def main():
    parser = argparse.ArgumentParser(
        description="Find and collect duplicate files for review."
    )
    parser.add_argument(
        '-d', '--directories',
        nargs='+',
        type=str,
        default=None,
        help="Directories to scan (default: ~/Downloads and ~)"
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help="Directory to move duplicates into (default: ~/Duplicates)"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show what would be moved without actually moving files"
    )
    args = parser.parse_args()

    # Set up scan directories
    if args.directories:
        scan_dirs = [Path(d).expanduser().resolve() for d in args.directories]
    else:
        scan_dirs = [Path.home() / "Downloads"]

    # Validate directories
    for d in scan_dirs:
        if not d.exists() or not d.is_dir():
            logging.error(f"Path {d} does not exist or is not a directory.")
            sys.exit(1)

    # Set up output directory
    if args.output:
        duplicates_dir = Path(args.output).expanduser().resolve()
    else:
        duplicates_dir = Path.home() / DUPLICATES_FOLDER

    logging.info(f"Scanning directories: {', '.join(str(d) for d in scan_dirs)}")
    if args.dry_run:
        logging.info("DRY RUN — no files will be moved.\n")

    # Collect and scan files
    files = collect_files(scan_dirs)
    duplicate_groups = find_duplicates(files)

    if not duplicate_groups:
        logging.info("\nNo duplicate files found.")
        return

    total_dupes = sum(len(g) - 1 for g in duplicate_groups)
    total_wasted = sum(
        sum(f.stat().st_size for f in g[1:])
        for g in duplicate_groups
    )
    logging.info(f"\nFound {len(duplicate_groups)} groups of duplicates ({total_dupes} duplicate files).")
    logging.info(f"Wasted space: {total_wasted / (1024 * 1024):.1f} MB")
    logging.info(f"{'Would move' if args.dry_run else 'Moving'} duplicates to: {duplicates_dir}\n")

    moved = move_duplicates(duplicate_groups, duplicates_dir, dry_run=args.dry_run)

    if not args.dry_run:
        logging.info(f"\nDone. {moved} duplicate files moved to {duplicates_dir}")
        logging.info("Review the Duplicates folder and delete files you no longer need.")


if __name__ == "__main__":
    main()
