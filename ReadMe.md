# 🧹 Downloads Folder Organizer

A Python script to automatically organize your macOS Downloads folder by sorting files into categorized subfolders based on their file types — helping you keep things clean and easy to navigate.

---

## 📂 What It Does

This script scans your `~/Downloads` directory and moves files into subfolders like:

- `Documents` — `.pdf`, `.docx`, `.txt`, etc.  
- `Images` — `.jpg`, `.png`, `.svg`, etc.  
- `Videos` — `.mp4`, `.mkv`, `.mov`, etc.  
- `Audio` — `.mp3`, `.wav`, `.m4a`, etc.  
- `Archives` — `.zip`, `.rar`, `.tar.gz`, etc.  
- `Scripts` — `.py`, `.js`, `.sh`, etc.  
- `Applications` — `.dmg`, `.pkg`, `.app`  
- `Others` — Anything else that doesn’t fit the above

Each file is moved into its appropriate folder. If a folder doesn't exist, it’s automatically created.

---

## 🚀 Getting Started

### Requirements

- Python 3.x  
- macOS 

### Installation

1. Clone the repository:

```bash
git https://github.com/cloudenochcsis/clean-my-downloads.git
cd clean-my-downloads

2. Run the script:
python3 organize_downloads.py
