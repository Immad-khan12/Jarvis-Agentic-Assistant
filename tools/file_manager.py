import os
from pathlib import Path

DOCUMENTS_DIR = Path.home() / "Documents"
DESKTOP_DIR = Path.home() / "Desktop"

def handle_file_operation(action: str, filename: str, content: str = "", location: str = "documents") -> str:
    """Handles local file creation, writing, appending, and reading."""
    target_dir = DESKTOP_DIR if location.lower() == "desktop" else DOCUMENTS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    
    if not any(filename.endswith(ext) for ext in [".txt", ".docx", ".json", ".csv", ".md"]):
        filename += ".txt"

    file_path = target_dir / filename

    try:
        if action in ["write", "create"]:
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
                    data = f.read()
                return f"📖 Content of '{filename}':\n{data}"
            else:
                return f"❌ File '{filename}' not found in {location.capitalize()}."

    except Exception as e:
        return f"❌ File operation failed: {str(e)}"

    return "Invalid operation requested."