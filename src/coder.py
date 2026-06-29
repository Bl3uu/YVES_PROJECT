import ollama

class Coder:
    """Handles deep technical analysis and code generation tasks.

    This class acts as a dedicated specialist module, leveraging a high-capacity 
    coding model to process context blocks and tasks without persona constraints.

    Attributes:
        model_name (str): The local Ollama identifier for the technical model instance.
    """

    def __init__(self, model_name: str = "qwen2.5-coder:7b") -> None:
        """Initialises the Coder module with a dedicated technical LLM."""
        self.model_name: str = model_name

    def analyze_code(self, context: str, task: str) -> str:
        """Executes zero-fluff technical analysis, bug fixing, or code generation.

        This method compiles local codebase context and the raw user task into 
        a performance-focused engineering prompt for the specialist model.

        Args:
            context (str): Relevant codebase strings retrieved from the vector database.
            task (str): The specific programming assignment or bug report from the user.

        Returns:
            str: Raw markdown code snippets or precise technical solutions.
        """
        prompt: str = f"""
CONTEXT FROM PROJECT FILES:
{context}

TASK:
{task}

INSTRUCTION: Provide a technical solution, code snippets, or bug fix. 
Be precise and optimize for performance.
"""
        
        response = ollama.chat(
            model=self.model_name,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content']