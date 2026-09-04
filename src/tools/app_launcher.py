import os
import platform
import subprocess
import webbrowser
from tools.tool_registry import registry


@registry.register(
    name="launch_app",
    description=(
        "Launches a local application (e.g., 'notepad', 'calculator', 'code')"
        " or opens a URL in the browser."
    ),
    parameters={
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": (
                    "The executable name/path (e.g., 'calc', 'notepad',"
                    " 'code') or full web URL (e.g., 'https://github.com')."
                ),
            }
        },
        "required": ["target"],
    },
)
def launch_app(target: str) -> str:
    """Opens a web URL or starts a background system process."""
    target_clean = target.strip()

    # Handle web URLs
    if target_clean.startswith(("http://", "https://")):
        webbrowser.open(target_clean)
        return f"Opened URL: {target_clean}"

    # Handle local executables across OS types
    try:
        system_os = platform.system()
        if system_os == "Windows":
            subprocess.Popen(f"start {target_clean}", shell=True)
        elif system_os == "Darwin":  # macOS
            subprocess.Popen(["open", "-a", target_clean])
        else:  # Linux
            subprocess.Popen([target_clean])

        return f"Successfully launched application: '{target_clean}'"
    except Exception as e:
        return f"Failed to launch '{target_clean}': {str(e)}"