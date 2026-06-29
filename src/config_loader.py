import os
from typing import Dict, Any
import yaml

class YvesConfig:
    """Parses and manages absolute system paths and model settings from configuration files.

    Dynamically resolves local runtime directories relative to this file's position, 
    preventing file path breaks across different operating system workspaces.

    Attributes:
        config_path (str): The explicit path to the target YAML file.
        data (Dict[str, Any]): Raw key-value configurations loaded from storage.
        BASE_DIR (str): The absolute root address of the project framework.
        INVENTORY_DIR (str): The directory containing files indexed by the vector manager.
        MEMORY_DIR (str): The folder containing the persistent ChromaDB collection.
        LOGIC_MODEL (str): Model name assigned to handle technical queries (Qwen).
        PERSONALITY_MODEL (str): Model name assigned to handle casual dialogue (Llama).
    """

    def __init__(self, config_path: str = None) -> None:
        """Initialises directory mapping attributes from YAML source files."""
        current_script_dir: str = os.path.dirname(os.path.abspath(__file__))
        
        if config_path is None:
            # Traverse out of src/ and into config/
            self.config_path: str = os.path.join(current_script_dir, "..", "config", "yves_config.yaml")
        else:
            self.config_path = config_path

        self.data: Dict[str, Any] = self._load_yaml()
        self.BASE_DIR: str = os.path.abspath(os.path.join(current_script_dir, ".."))
        
        paths: Dict[str, str] = self.data.get('paths', {})
        self.INVENTORY_DIR: str = os.path.join(self.BASE_DIR, paths.get('inventory', 'data/inventory'))
        self.MEMORY_DIR: str = os.path.join(self.BASE_DIR, paths.get('memory', 'data/memory'))
        
        models: Dict[str, str] = self.data.get('models', {})
        self.LOGIC_MODEL: str = models.get('logic', 'qwen2.5-coder:7b')
        self.PERSONALITY_MODEL: str = models.get('personality', 'llama3.2:3b')

    def _load_yaml(self) -> Dict[str, Any]:
        """Reads configuration metrics from the assigned YAML location paths.

        Returns:
            Dict[str, Any]: The configuration parameter tree or an empty dictionary if missing.
        """
        if not os.path.exists(self.config_path):
            print(f"Warning: {self.config_path} not found. Using system fallback defaults.")
            return {}
            
        with open(self.config_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
            return config_data if config_data is not None else {}