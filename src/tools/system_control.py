from datetime import datetime
import os
import mss
from tools.tool_registry import registry


@registry.register(
    name="take_screenshot",
    description=(
        "Captures a screenshot of the primary display and saves it to disk."
    ),
    parameters={
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": (
                    "Optional file name. If omitted, uses a timestamped PNG."
                ),
            }
        },
        "required": [],
    },
)
def take_screenshot(filename: str = "") -> str:
  """Captures and saves a primary screen image."""
  try:
    if not filename:
      timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
      filename = f"screenshot_{timestamp}.png"

    with mss.mss() as sct:
      # Grab primary monitor (monitor 1)
      sct.shot(mon=1, output=filename)

    filepath = os.path.abspath(filename)
    return f"Screenshot captured successfully: {filepath}"
  except Exception as e:
    return f"Failed to capture screenshot: {str(e)}"