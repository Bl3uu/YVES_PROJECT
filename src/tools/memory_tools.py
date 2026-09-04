from memory.vector_memory import memory_engine
from tools.tool_registry import registry


@registry.register(
    name="remember_fact",
    description=(
        "Saves key facts, user preferences, or project details into long-term"
        " vector memory for future recall."
    ),
    parameters={
        "type": "object",
        "properties": {
            "fact": {
                "type": "string",
                "description": (
                    "The specific factual statement or note to commit to memory."
                ),
            }
        },
        "required": ["fact"],
    },
)
def remember_fact(fact: str) -> str:
  """Exposes explicit fact storage to YVES."""
  return memory_engine.store(fact)