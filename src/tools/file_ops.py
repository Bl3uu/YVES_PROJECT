import os
from datetime import datetime
from tools.tool_registry import registry

@registry.register(
    name="list_files",
    description="Lists all files and directories inside a target directory path.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Relative or absolute directory path to inspect. Defaults to current workspace ('.')."
            }
        },
        "required": []
    }
)
def list_files(path: str = ".") -> str:
    """Lists files and folders at a target path."""
    try:
        target_path = os.path.abspath(path)
        if not os.path.exists(target_path):
            return f"Error: Path '{path}' does not exist."
        if not os.path.isdir(target_path):
            return f"Error: Path '{path}' is a file, not a directory."

        entries = os.listdir(target_path)
        if not entries:
            return f"Directory '{path}' is empty."

        formatted_entries = []
        for entry in entries:
            full_entry_path = os.path.join(target_path, entry)
            is_dir = "[DIR]" if os.path.isdir(full_entry_path) else "[FILE]"
            formatted_entries.append(f"{is_dir} {entry}")

        return f"Contents of '{path}':\n" + "\n".join(formatted_entries)
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@registry.register(
    name="read_file",
    description="Reads and returns the text content of a file.",
    parameters={
        "type": "object",
        "properties": {
            "filepath": {
                "type": "string",
                "description": "Path to the file to read."
            }
        },
        "required": ["filepath"]
    }
)
def read_file(filepath: str) -> str:
    """Reads content from a target file."""
    try:
        abs_path = os.path.abspath(filepath)
        if not os.path.exists(abs_path):
            return f"Error: File '{filepath}' not found."
        
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if len(content) > 4000:
            return f"File '{filepath}' read successfully (truncated to first 4000 chars):\n\n" + content[:4000] + "\n\n... [Truncated]"
        return f"File '{filepath}' content:\n\n" + content
    except Exception as e:
        return f"Error reading file '{filepath}': {str(e)}"


@registry.register(
    name="write_file",
    description="Writes text content to a file. Overwrites existing content unless specified.",
    parameters={
        "type": "object",
        "properties": {
            "filepath": {
                "type": "string",
                "description": "Path to the file to create or overwrite."
            },
            "content": {
                "type": "string",
                "description": "Text or code content to write into the file."
            }
        },
        "required": ["filepath", "content"]
    }
)
def write_file(filepath: str, content: str) -> str:
    """Writes text to a specified file path."""
    try:
        abs_path = os.path.abspath(filepath)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return f"Successfully wrote content to '{filepath}'."
    except Exception as e:
        return f"Error writing file '{filepath}': {str(e)}"