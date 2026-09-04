from typing import Any, Callable, Dict, List


class ToolRegistry:
  """Central registry for managing and invoking local YVES tools."""

  def __init__(self) -> None:
    self._tools: Dict[str, Callable] = {}
    self._schemas: List[Dict[str, Any]] = []

  def register(self, name: str, description: str, parameters: Dict[str, Any]):
    """Decorator to register a python function as an executable tool."""

    def decorator(func: Callable):
      self._tools[name] = func
      self._schemas.append({
          'type': 'function',
          'function': {
              'name': name,
              'description': description,
              'parameters': parameters,
          },
      })
      return func

    return decorator

  def get_schemas(self) -> List[Dict[str, Any]]:
    """Returns tool schema definitions for the Ollama API."""
    return self._schemas

  def execute(self, tool_name: str, arguments: Dict[str, Any]) -> str:
    """Executes the mapped function and returns string output."""
    if tool_name not in self._tools:
      return f"Error: Tool '{tool_name}' is not registered."
    try:
      return str(self._tools[tool_name](**arguments))
    except Exception as e:
      return f"Error executing '{tool_name}': {str(e)}"


# Global registry instance shared across all tools
registry = ToolRegistry()