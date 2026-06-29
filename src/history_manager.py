from collections import deque
from typing import List, Dict

class HistoryManager:
    """Manages the short-term conversation memory buffer for the AI engine.

    This class acts as a rolling FIFO (First-In, First-Out) queue using a deque
    to ensure the LLM retains context of recent interactions without exceeding 
    the token window constraints.

    Attributes:
        buffer (deque): A thread-safe, double-ended queue storing message frames.
    """

    def __init__(self, max_limit: int = 10) -> None:
        """Initialises the HistoryManager with a strict buffer size constraint.

        Args:
            max_limit (int): The maximum number of historical messages to retain 
                before old entries are dropped. Defaults to 10.
        """
        # setting maxlen automatically drops the oldest entry when new items are appended
        self.buffer: deque = deque(maxlen=max_limit)

    def add_entry(self, role: str, content: str) -> None:
        """Adds a new message exchange to the history buffer.

        Args:
            role (str): The author of the message ('user' or 'assistant').
            content (str): The literal text payload of the message.
        """
        self.buffer.append({"role": role, "content": content})

    def get_transcript(self) -> List[Dict[str, str]]:
        """Retrieves the full stored chat history as a standard list.

        Ollama requires a standard list format for processing messages, 
        so the internal deque is cast back to a list during retrieval.

        Returns:
            List[Dict[str, str]]: The active conversation history entries.
        """
        return list(self.buffer)