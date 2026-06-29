import subprocess

class Terminal:
    """Executes local operating system terminal commands from the AI pipeline.

    This class provides YVES with system execution utility, allowing her 
    to interact directly with the host machine's shell environment.
    """

    def __init__(self) -> None:
        """Initialises the Terminal execution component."""
        pass

    def execute(self, command: str) -> str:
        """Runs a command string in the host system shell and returns the output.

        Args:
            command (str): The literal shell command line text string to execute.

        Returns:
            str: The standard output string from a successful execution, 
                or the error trace if the command fails.
        """
        try:
            # shell=True allows standard terminal expressions and command piping
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "System Execution Failed: Command execution timed out after 30 seconds."
        except Exception as e:
            return f"System Execution Failed: {str(e)}"