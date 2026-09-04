import os
from typing import Any, Dict
import yaml


class YvesConfig:
  """Parses and manages system paths and model settings from yves_config.yaml."""

  def __init__(self, config_path: str = None) -> None:
    current_script_dir: str = os.path.dirname(os.path.abspath(__file__))

    if config_path is None:
      self.config_path: str = os.path.join(
          current_script_dir, "..", "config", "yves_config.yaml"
      )
    else:
      self.config_path = config_path

    self.BASE_DIR: str = os.path.abspath(
        os.path.join(current_script_dir, "..")
    )
    self.data: Dict[str, Any] = self._load_yaml()

    # Settings
    models: Dict[str, Any] = self.data.get("models", {})
    settings: Dict[str, Any] = self.data.get("settings", {})

    self.CORE_MODEL: str = models.get("core", "qwen2.5:7b")
    self.TEMPERATURE: float = settings.get("temperature", 0.7)
    self.MAX_HISTORY: int = settings.get("max_history", 10)

  def _load_yaml(self) -> Dict[str, Any]:
    if not os.path.exists(self.config_path):
      print(
          f"Warning: {self.config_path} not found. Using system fallback"
          " defaults."
      )
      return {}

    with open(self.config_path, "r", encoding="utf-8") as file:
      config_data = yaml.safe_load(file)
      return config_data if config_data is not None else {}