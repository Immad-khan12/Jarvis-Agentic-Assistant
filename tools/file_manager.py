import os
from pathlib import Path

DOCUMENTS_DIR = Path.home() / "Documents"
DESKTOP_DIR = Path.home() / "Desktop"

def handle_file_operation(action: str, filename: str, content: str = "", location: str = "documents") -> str:
    """Handles local file creation, writing, appending, and reading."""
    location_key = location.strip().lower()
    known_locations = {
        "desktop": DESKTOP_DIR,
        "documents": DOCUMENTS_DIR,
        "downloads": Path.home() / "Downloads",
        "pictures": Path.home() / "Pictures",
        "videos": Path.home() / "Videos",
        "music": Path.home() / "Music",
    }
    target_dir = known_locations.get(location_key, Path(location).expanduser())
    home_dir = Path.home().resolve()
    try:
        target_dir = target_dir.resolve()
        target_dir.relative_to(home_dir)
    except ValueError:
        return "❌ Sirf user profile ke andar folders allowed hain."
    target_dir.mkdir(parents=True, exist_ok=True)

    if action == "list":
        entries = sorted(item.name for item in target_dir.iterdir())[:100]
        if not entries:
            return f"📁 {location} folder empty hai."
        return f"📁 {location} mein: " + ", ".join(entries)

    if not filename:
        return "❌ File name required hai."

    requested_path = Path(filename)
    if requested_path.is_absolute():
        return "❌ Filename relative hona chahiye; folder location alag field mein dein."
    
    if action not in {"rename", "delete"} and not any(filename.lower().endswith(ext) for ext in [".txt", ".json", ".csv", ".md", ".py", ".html", ".css", ".js"]):
        filename += ".txt"

    file_path = (target_dir / filename).resolve()
    try:
        file_path.relative_to(target_dir)
    except ValueError:
        return "❌ Filename selected folder ke bahar nahi ja sakta."
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if action == "rename":
            new_filename = content.strip()
            new_path = (target_dir / new_filename).resolve()
            new_path.relative_to(target_dir)
            if new_path.exists():
                return "❌ New file name already exists."
            if not file_path.exists():
                return f"❌ File '{filename}' not found."
            file_path.rename(new_path)
            return f"✅ '{filename}' ka naam '{new_filename}' kar diya."

        if action == "delete":
            if os.getenv("JARVIS_ALLOW_FILE_DELETE") != "1":
                return "❌ File delete disabled hai. JARVIS_ALLOW_FILE_DELETE=1 set karna hoga."
            if not file_path.exists() or not file_path.is_file():
                return f"❌ File '{filename}' not found."
            file_path.unlink()
            return f"✅ File '{filename}' delete kar di."

        if action == "create":
            if file_path.exists():
                return f"❌ File '{filename}' already exists. Overwrite ke liye write/edit command dein."
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"✅ File '{filename}' successfully created and saved in {location.capitalize()} folder."

        if action == "write":
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"✅ File '{filename}' successfully created and saved in {location.capitalize()} folder."
        
        elif action == "append":
            with open(file_path, "a", encoding="utf-8") as f:
                f.write("\n" + content)
            return f"✅ Content added to '{filename}' in {location.capitalize()}."

        elif action == "read":
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    data = f.read(20000)
                return f"📖 Content of '{filename}':\n{data}"
            else:
                return f"❌ File '{filename}' not found in {location.capitalize()}."

    except Exception as e:
        return f"❌ File operation failed: {str(e)}"

    return "Invalid operation requested."