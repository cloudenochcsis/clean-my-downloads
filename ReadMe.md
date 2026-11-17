# Clean My Downloads Organizer

A Python script to automatically organize your macOS Downloads folder by moving files and loose course/movie directories into smart, categorized subfolders (e.g., PhD Research, Job Hunting Resumes, Documents, Books & Guides, Images, Videos, Courses).

---

## Features

- **Semantic & Pattern Categorization**: Understands context beyond just file extensions (e.g. PhD proposal/defence revisions, job applications, textbooks, database backups, tickets).
- **Consolidates Loose Folders**: Automatically moves course directories (Udemy, Mosh, DevOps) into `Courses/` and movie directories into `Videos/`.
- **Smart Duplicate Hashing**: Detects bit-for-bit duplicate files using MD5 and safely routes duplicates to `redundant files/` instead of cluttering your working folders.
- **Safety Buffer**: Skips in-progress downloads (`.crdownload`, `.part`, `.tmp`) and recently modified files (< 120s old) to never disrupt active downloads.
- **Dry-Run Preview**: Test what would happen with `--dry-run` before anything is moved.
- **Automated via macOS LaunchAgent**: Scheduled to run 3 times a week (Monday, Wednesday, Friday at 10:00 AM) using native `launchd`.
- **Zero External Dependencies**: Pure Python standard library (`pathlib`, `shutil`, `hashlib`, `argparse`).

---

## Supported Categories & Routing

| Category / Folder | Triggers & Examples |
| :--- | :--- |
| **PhD Research** | Keywords: `proposal`, `panel feedback`, `phd defence`, `correction matrix`, `schedule of corrections` |
| **Job Hunting Resumes** | Keywords: `resume`, `cv`, `job spec`, `application`, `motivation letter`, `personal history` |
| **Courses** | Directories matching: `Udemy`, `Code with Mosh`, `Learn DevOps`, `Kubernetes Course`, `GitHub Actions` |
| **Documents/Books & Guides** | Keywords: `CompTIA`, `CySA+`, `Exam Guide`, `Review Guide`, `SACLA_`, `libgen`, or extensions `.epub`, `.azw` |
| **Documents/Personal & Admin** | Keywords: `ticket`, `payment notification`, `proof of registration`, `source of income`, `recovery-codes` |
| **Documents/Database Backups**| Extensions `.sql`, `.dump`, or filenames containing `_backup.`, `_db_backup` |
| **Applications** | `.dmg`, `.pkg`, `.app` |
| **Archives** | `.zip`, `.tar`, `.gz`, `.tgz`, `.rar`, `.7z` |
| **Images** | `.jpg`, `.jpeg`, `.png`, `.gif`, `.svg`, `.webp`, `.heic`, `.heif` |
| **Videos** | Files (`.mp4`, `.mov`, `.mkv`) and movie directories (`1080p`, `720p`, `WEB-DL`, `WEBRip`) |
| **Audio** | `.mp3`, `.wav`, `.m4a`, `.aac`, `.flac` |
| **redundant files** | Byte-identical duplicate files, duplicate installers, and orphaned Word lock files (`~$...`) |
| **Documents (General)** | Standard `.pdf`, `.docx`, `.xlsx`, `.pptx`, `.txt`, `.csv` |

---

## Usage

### Run Live
```bash
python3 organize_downloads.py
```

### Dry Run (Preview without moving)
```bash
python3 organize_downloads.py --dry-run
```

### Custom Directory or Custom Age Buffer
```bash
python3 organize_downloads.py -d /path/to/folder --min-age 300
```

### Run Tests
```bash
python3 -m unittest test_organize_downloads.py
```

---

## Automation (macOS LaunchAgent)

The repository includes `com.user.organize-downloads.plist`, scheduled to run **Monday, Wednesday, and Friday at 10:00 AM**.

To install and load:
```bash
cp com.user.organize-downloads.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.user.organize-downloads.plist
```

To check status:
```bash
launchctl list | grep "com.user.organize-downloads"
```

Logs are written to:
- `organize_downloads.log`
- `organize_downloads_error.log`

---

## License

This project is open source and available under the [MIT License](LICENSE).
