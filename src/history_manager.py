from typing import Dict, List


class HistoryManager:
  """Manages short-term sliding window conversation context."""

  def __init__(self, max_limit: int = 10) -> None:
    self.max_limit: int = max_limit
    self.history: List[Dict[str, str]] = []

  def add_turn(self, user_message: str, assistant_message: str) -> None:
    """Appends a completed interaction turn to the history array."""
    self.history.append({"role": "user", "content": user_message})
    self.history.append({"role": "assistant", "content": assistant_message})
    self._trim_history()

  def get_history(self) -> List[Dict[str, str]]:
    """Returns the current formatted conversation logs."""
    return self.history

  def clear(self) -> None:
    """Wipes active session conversation logs."""
    self.history.clear()

  def _trim_history(self) -> None:
    """Enforces the sliding window limit (2 entries per turn: user + assistant)."""
    max_entries = self.max_limit * 2
    if len(self.history) > max_entries:
      self.history = self.history[-max_entries:]