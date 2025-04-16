# Clean My Downloads Organizer

A Python script to automatically organize your macOS Downloads folder by moving files into categorized subfolders (e.g., Documents, Images, Videos). This helps keep your workspace tidy and makes files easier to find.

---

## Features

- **Skips hidden/system files** (e.g., `.DS_Store`, files starting with a dot)
- **Prevents overwriting**: If a file with the same name exists, a number is appended (e.g., `file (1).pdf`)
- **Categorizes by file type**: Documents, Images, Videos, Audio, Archives, Scripts, Applications, Others
- **Modern path handling**: Uses `pathlib` for reliability and readability
- **Logging**: Informative logs for each action (can be easily redirected to a file)
- **Ignores in-progress downloads**: Skips files like `.part`, `.crdownload`, `.tmp`
- **Customizable**: Organize any directory, not just Downloads
- **No external dependencies**: Pure Python standard library

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/cloudenochcsis/clean-my-downloads.git
   cd clean-my-downloads
   ```
2. (Optional) Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. No dependencies to install—uses only the Python standard library.

---

## Usage

### Organize your Downloads folder
```bash
python organize_downloads.py
```

### Organize a custom directory
```bash
python organize_downloads.py --directory /path/to/your/folder
```

### Example Output
```
Moved: resume.pdf → Documents
Moved: vacation.jpg → Images
Moved: script.py → Scripts
```

---

## How It Works
- Each file is checked for its extension and moved to the corresponding category folder.
- If the folder does not exist, it is created automatically.
- Hidden/system files and in-progress downloads are skipped.
- If a file with the same name exists, a new name is generated (e.g., `file (1).pdf`).

---

## Supported Categories
- **Documents:** .pdf, .doc, .docx, .txt, .xls, .xlsx, .ppt, .pptx
- **Images:** .jpg, .jpeg, .png, .gif, .bmp, .tiff, .svg
- **Videos:** .mp4, .mov, .avi, .mkv, .flv, .wmv
- **Audio:** .mp3, .wav, .m4a, .aac, .ogg
- **Archives:** .zip, .tar, .gz, .rar, .7z
- **Scripts:** .py, .js, .sh, .rb, .pl
- **Applications:** .dmg, .pkg, .app
- **Others:** Everything else

---

## Contributing

Pull requests and suggestions are welcome! To contribute:
1. Fork this repository
2. Create your feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a pull request

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

**Status:** Alpha. Use at your own risk. Feedback welcome!

