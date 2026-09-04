import platform
import psutil
from tools.tool_registry import registry


@registry.register(
    name="get_system_stats",
    description=(
        "Retrieves system hardware specs and real-time metrics (RAM, CPU, Disk,"
        " OS)."
    ),
    parameters={
        "type": "object",
        "properties": {
            "metric": {
                "type": "string",
                "description": (
                    "The metric or summary to retrieve: 'all' for full specs,"
                    " or 'ram', 'cpu', 'disk'."
                ),
                "enum": ["all", "ram", "cpu", "disk"],
            }
        },
        "required": ["metric"],
    },
)
def get_system_stats(metric: str = "all") -> str:
  """Fetches system specs and utilization stats."""
  mem = psutil.virtual_memory()
  total_ram_gb = round(mem.total / (1024**3), 2)
  used_ram_gb = round(mem.used / (1024**3), 2)

  cpu_count = psutil.cpu_count(logical=True)
  cpu_percent = psutil.cpu_percent(interval=0.2)
  processor_name = platform.processor() or "Unknown CPU"

  disk = psutil.disk_usage("/")
  total_disk_gb = round(disk.total / (1024**3), 2)
  free_disk_gb = round(disk.free / (1024**3), 2)

  if metric == "ram":
    return (
        f"RAM: {mem.percent}% used ({used_ram_gb} GB / {total_ram_gb} GB total)"
    )
  elif metric == "cpu":
    return (
        f"CPU: {processor_name} ({cpu_count} logical cores) - Utilization:"
        f" {cpu_percent}%"
    )
  elif metric == "disk":
    return f"Disk: {disk.percent}% used ({free_disk_gb} GB free / {total_disk_gb} GB total)"
  else:
    # 'all' - Overview
    return (
        f"OS: {platform.system()} {platform.release()} | "
        f"CPU: {processor_name} ({cpu_count} cores) at {cpu_percent}% usage | "
        f"RAM: {total_ram_gb} GB Total ({mem.percent}% used) | "
        f"Disk: {total_disk_gb} GB Total ({free_disk_gb} GB free)"
    )