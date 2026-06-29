import datetime
import platform
from typing import Dict, Any

# Explicit imports ensure clean compilation paths
from identity import YvesIdentity
from history_manager import HistoryManager
from retriever import MemoryVault
from coder import Coder

class YvesEngine:
    """The central orchestrator of the Virtual Engineering System.

    YvesEngine implements structural routing logic. It intercepts user inputs, 
    evaluates technical intent thresholds, and matches execution to the design flowchart.
    """

    def __init__(self, identity: YvesIdentity, coder: Coder, vault: MemoryVault, history: HistoryManager) -> None:
        """Initialises the core engine with explicitly injected sub-module dependencies."""
        self.identity: YvesIdentity = identity
        self.coder: Coder = coder
        self.vault: MemoryVault = vault
        self.history: HistoryManager = history

    def ask(self, user_query: str) -> str:
        """Processes a raw user input through the core routing and modular pipeline.

        Args:
            user_query (str): The literal raw string input from the user.

        Returns:
            str: The final system output string ready for rendering.
        """
        # Gather spatial awareness details
        situation: Dict[str, Any] = {
            "time": datetime.datetime.now().strftime("%H:%M"),
            "day": datetime.datetime.now().strftime("%A"),
            "os": platform.system()
        }

        # Intent Classification matches the diagram precisely
        if self._route_intent(user_query):
            # 1. Pull matches from the vector database
            context_chunks = self.vault.search(user_query)
            
            # 2. Context Guard: Check if the database actually returned anything
            if context_chunks and len(context_chunks) > 0:
                # Join list items into a single context string block
                context = "\n---\n".join(context_chunks)
                
                # Proceed with normal technical pipeline execution
                tech_data = self.coder.analyze_code(context, user_query)
                response = self.identity.generate_technical_response(
                    tech_data, user_query, self.history.get_transcript(), situation
                )
            else:
                # Fall back to casual mode if the database has no knowledge of the files
                fallback_query = f"[System Notification: You cannot access files for this query because the context database is empty. Inform the user politely without breaking character]. User said: {user_query}"
                response = self.identity.generate_casual_response(
                    fallback_query, self.history.get_transcript(), situation
                )
        else:
            # Standard casual path
            response = self.identity.generate_casual_response(
                user_query, self.history.get_transcript(), situation
            )

        # Commit conversation states to memory AFTER generation, not before
        self.history.add_entry("user", user_query)
        self.history.add_entry("assistant", response)
        return response

    def _route_intent(self, query: str) -> bool:
        """Evaluates whether an incoming statement requires deep technical execution.

        Args:
            query (str): The incoming text string to process.

        Returns:
            bool: True if the query maps semantically to engineering tasks, False otherwise.
        """
        # Use the vector math database to classify the intent category
        intent_category = self.vault.predict_intent(query)
        return intent_category == "technical"