"""
system_executor.py — Lets Jarvis run ANY Windows/PowerShell command via voice,
giving near-full OS control instead of being limited to pre-built tools.

WHY THIS EXISTS:
Every other tool (open_anything, system_control, etc.) covers ONE specific
action. This tool is the "catch-all" — if the user asks for something no
other tool handles, the LLM can fall back to this and just run the raw
command needed to do it.

SAFETY:
Because a voice-transcribed, AI-interpreted command could contain mistakes,
this tool refuses to run anything that matches a list of clearly destructive
patterns (formatting drives, mass-deleting system folders, etc.) — even if
asked. Everything else runs as normal. You can expand/edit the blocklist
below as you see fit.
"""

import subprocess

# Patterns that are ALWAYS blocked, no matter how they're phrased.
# Add more here if you think of other dangerous commands.
DANGEROUS_PATTERNS = [
    "format ",
    "diskpart",
    "del /s /q c:\\",
    "del /f /s /q c:\\",
    "rd /s /q c:\\",
    "rmdir /s /q c:\\",
    "remove-item c:\\ -recurse",
    "remove-item c:\\* -recurse",
    "shutdown /s /f /t 0",  # instant forced shutdown with no warning
    "reg delete hklm",
    "vssadmin delete shadows",
    "cipher /w",
    "bcdedit",
    "attrib -h -s",  # commonly used to unhide/attack system files
]


def _is_dangerous(command: str) -> bool:
    lowered = command.lower()
    return any(pattern in lowered for pattern in DANGEROUS_PATTERNS)


def run_system_command(command: str) -> str:
    """
    Executes an arbitrary PowerShell command and returns its output.
    Use this as a fallback for OS-level requests that no specific tool covers
    — e.g. renaming a file, checking disk space, listing running processes,
    changing a specific setting, killing a process by name, etc.
    """
    if not command or not command.strip():
        return "❌ Koi command nahi di gayi."

    if _is_dangerous(command):
        return "❌ Ye command potentially destructive hai (drive format/delete jaisa kuch), safety ke liye block kar diya gaya hai."

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode != 0:
            return f"❌ Command error: {error or 'unknown error'}"

        if output:
            # Keep spoken responses short — truncate very long outputs
            if len(output) > 500:
                output = output[:500] + "... (output truncated)"
            return f"✅ Done:\n{output}"

        return "✅ Command successfully run ho gayi."

    except subprocess.TimeoutExpired:
        return "❌ Command 30 second se zyada le rahi thi, ruk gayi."
    except Exception as e:
        return f"❌ Execution error: {str(e)}"