import shutil
import logging
import argparse
import sys
import time
import hashlib
from pathlib import Path

# Base file type extension categories (used as fallback)
file_types = {
    "Applications": [".dmg", ".pkg", ".app"],
    "Archives": [".zip", ".tar", ".gz", ".tgz", ".rar", ".7z", ".bz2"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".webp", ".heic", ".heif"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv"],
    "Audio": [".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"],
    "Scripts": [".py", ".js", ".sh", ".rb", ".pl"],
    "Others": []
}

# Known top-level categories that should never be moved into other folders
PROTECTED_TOP_LEVEL_DIRS = {
    "applications", "archives", "audio", "courses", "documents",
    "images", "job hunting resumes", "lr samples", "phd research",
    "videos", "zotero papers", "cloudenoch_com", "kiddie-product-images",
    "redundant files"
}

# Extensions that indicate in-progress downloads
IN_PROGRESS_EXTS = [".part", ".crdownload", ".tmp", ".download"]

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def is_hidden_or_system(file_path: Path) -> bool:
    """Return True if the file is hidden or a common system file."""
    return file_path.name.startswith('.') or file_path.name in {'.DS_Store', '.localized', 'Thumbs.db'}


def is_in_progress(file_path: Path) -> bool:
    """Return True if the file looks like an in-progress download."""
    name_lower = file_path.name.lower()
    return any(name_lower.endswith(ext) for ext in IN_PROGRESS_EXTS)


def is_recent(file_path: Path, min_age_seconds: int = 120) -> bool:
    """Return True if the file was modified within min_age_seconds."""
    try:
        mtime = file_path.stat().st_mtime
        return (time.time() - mtime) < min_age_seconds
    except (OSError, PermissionError):
        return False


def hash_file(file_path: Path, chunk_size: int = 8192) -> str:
    """Calculate and return MD5 hash of file."""
    if not file_path.is_file():
        return ""
    h = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, PermissionError):
        return ""


def classify_item(item_path: Path, is_dir: bool = False) -> str:
    """Classify a file or directory into a target category subfolder."""
    name = item_path.name
    name_lower = name.lower()

    # Orphaned Word temporary lock files
    if name.startswith("~$"):
        return "redundant files"

    if is_dir:
        # Do not move protected top-level category directories
        if name_lower.strip() in PROTECTED_TOP_LEVEL_DIRS:
            return ""

        # Courses & Tutorials
        course_keywords = [
            "udemy", "code with mosh", "learn devops", "kubernetes course",
            "github actions", "bootcamp", "masterclass", "vibe coding"
        ]
        if any(kw in name_lower for kw in course_keywords):
            return "Courses"

        # Movie directories
        movie_patterns = ["1080p", "720p", "2160p", "web-dl", "webrip", "bluray", "dcprip", "remux"]
        if any(pat in name_lower for pat in movie_patterns):
            return "Videos"

        return ""

    # 1. PhD Research documents
    phd_keywords = [
        "proposal", "panel feedback", "panel_feedback", "phd defence",
        "phd_defence", "correction matrix", "corrections_phd",
        "corrections tracked", "correctionslocal", "second_corrections",
        "schedule of corrections"
    ]
    if any(kw in name_lower for kw in phd_keywords):
        return "PhD Research"

    # 2. Job Hunting Resumes & Applications
    job_keywords = [
        "resume", "cv", "job spec", "application", "motivation letter",
        "motivation_letter", "personal history", "personal_history",
        "cover letter"
    ]
    if any(kw in name_lower for kw in job_keywords):
        return "Job Hunting Resumes"

    # 3. Database backups
    if item_path.suffix.lower() in [".sql", ".dump"] or "_backup." in name_lower or "_db_backup" in name_lower:
        return "Documents/Database Backups"

    # 4. Books, Textbooks & Academic Proceedings
    book_exts = [".epub", ".azw", ".azw3", ".mobi"]
    book_keywords = [
        "exam guide", "review guide", "student guide", "libgen", "proceedings",
        "comptia", "cysa+", "sacla_", "managing the digital firm"
    ]
    if item_path.suffix.lower() in book_exts or any(kw in name_lower for kw in book_keywords):
        return "Documents/Books & Guides"

    # 5. Personal, Admin & Financial documents
    admin_keywords = [
        "ticket", "tickets", "payment notification", "proof of registration",
        "source of income", "income declaration", "recovery-codes", "ref022208676",
        "agreement of lease", "admission letter", "admissionletter"
    ]
    if any(kw in name_lower for kw in admin_keywords):
        return "Documents/Personal & Admin"

    # 6. Fallback file type extension categories
    file_ext = item_path.suffix.lower()
    for folder, extensions in file_types.items():
        if file_ext in extensions:
            return folder

    return "Others"


def get_unique_destination(dest_folder: Path, file_name: str) -> Path:
    """Return a unique file path in dest_folder to avoid overwriting differing files."""
    dest_file = dest_folder / file_name
    if not dest_file.exists():
        return dest_file
    stem = dest_file.stem
    suffix = dest_file.suffix
    i = 1
    while True:
        candidate = dest_folder / f"{stem} ({i}){suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def resolve_destination(downloads_path: Path, dest_folder: Path, src_path: Path) -> Path:
    """Resolve destination path, handling exact duplicate hashes safely."""
    dest_file = dest_folder / src_path.name
    if not dest_file.exists():
        return dest_file

    # File exists at destination. Check if it is an exact duplicate by hash
    src_hash = hash_file(src_path)
    dest_hash = hash_file(dest_file)

    if src_hash and dest_hash and src_hash == dest_hash:
        # Exact duplicate! Move to redundant files instead of cluttering target folder
        redundant_dir = downloads_path / "redundant files"
        redundant_dir.mkdir(parents=True, exist_ok=True)
        dup_name = f"{src_path.stem} (duplicate){src_path.suffix}"
        return get_unique_destination(redundant_dir, dup_name)

    # Different content or unhashable: preserve by generating a unique name
    return get_unique_destination(dest_folder, src_path.name)


def organize_item(item_path: Path, downloads_path: Path, min_age_seconds: int = 120, dry_run: bool = False):
    """Organize a single file or directory into its destination."""
    if is_hidden_or_system(item_path):
        return
    if is_in_progress(item_path):
        logging.info(f"Skipping in-progress download: {item_path.name}")
        return
    if item_path.is_file() and is_recent(item_path, min_age_seconds):
        logging.info(f"Skipping recent file (<{min_age_seconds}s old): {item_path.name}")
        return

    category = classify_item(item_path, is_dir=item_path.is_dir())
    if not category:
        return

    dest_folder = downloads_path / category
    if not dry_run:
        dest_folder.mkdir(parents=True, exist_ok=True)

    dest_target = resolve_destination(downloads_path, dest_folder, item_path)

    if dry_run:
        logging.info(f"[DRY-RUN] Would move: {item_path.name} -> {dest_target.relative_to(downloads_path)}")
    else:
        try:
            shutil.move(str(item_path), str(dest_target))
            logging.info(f"Moved: {item_path.name} -> {dest_target.relative_to(downloads_path)}")
        except Exception as e:
            logging.error(f"Failed to move {item_path.name}: {e}")


def organize_downloads(downloads_path: Path, min_age_seconds: int = 120, dry_run: bool = False):
    """Scan and organize all qualifying items in the downloads folder."""
    logging.info(f"Starting organization for: {downloads_path} (dry_run={dry_run})")
    count = 0
    # Collect items first to prevent directory iterator modification issues
    items = list(downloads_path.iterdir())
    for item in items:
        # Only process top-level items directly inside downloads
        if item.parent == downloads_path:
            organize_item(item, downloads_path, min_age_seconds=min_age_seconds, dry_run=dry_run)
            count += 1
    logging.info(f"Scan finished. Processed {count} items.")


def main():
    parser = argparse.ArgumentParser(description="Smart Downloads organizer with semantic rules and deduplication.")
    parser.add_argument(
        '-d', '--directory',
        type=str,
        default=str(Path.home() / "Downloads"),
        help="Directory to organize (default: ~/Downloads)"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Simulate actions without moving any files"
    )
    parser.add_argument(
        '--min-age',
        type=int,
        default=120,
        help="Minimum file age in seconds to move (default: 120)"
    )
    args = parser.parse_args()

    downloads_path = Path(args.directory).expanduser().resolve()
    if not downloads_path.exists() or not downloads_path.is_dir():
        logging.error(f"Provided path {downloads_path} does not exist or is not a directory.")
        sys.exit(1)

    organize_downloads(downloads_path, min_age_seconds=args.min_age, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
