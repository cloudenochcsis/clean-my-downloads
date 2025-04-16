import os
import shutil

# Define the path to your Downloads folder
downloads_path = os.path.expanduser("~/Downloads")

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

def move_file(file_name):
    file_path = os.path.join(downloads_path, file_name)
    if os.path.isdir(file_path):
        return  # skip directories

    file_ext = os.path.splitext(file_name)[1].lower()

    # Determine category
    destination_folder = "Others"
    for folder, extensions in file_types.items():
        if file_ext in extensions:
            destination_folder = folder
            break

    destination_path = os.path.join(downloads_path, destination_folder)

    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    try:
        shutil.move(file_path, os.path.join(destination_path, file_name))
        print(f"Moved: {file_name} → {destination_folder}")
    except Exception as e:
        print(f"Failed to move {file_name}: {e}")

def organize_downloads():
    for file in os.listdir(downloads_path):
        move_file(file)

if __name__ == "__main__":
    organize_downloads()
