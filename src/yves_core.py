from datetime import datetime
import platform
from typing import Any, Dict, Generator
import ollama

from history_manager import HistoryManager
from tools.app_launcher import launch_app
from tools.file_ops import list_files, read_file, write_file
from tools.system_control import take_screenshot
from tools.system_info import get_system_stats
from tools.tool_registry import registry
from tools.web_search import web_search 
from yves_config import YvesConfig


class YvesCore:
  """Unified core engine for YVES.

  Handles persona directives, situational context injection, tool calling, and
  direct inference calls to local Ollama instances.
  """

  def __init__(
      self,
      config: YvesConfig = None,
      history: HistoryManager = None,
      user_name: str = "Dustin",
      location: str = "Santo Tomas, Philippines",
  ) -> None:
    self.config: YvesConfig = config if config else YvesConfig()
    self.history: HistoryManager = (
        history if history else HistoryManager(max_limit=self.config.MAX_HISTORY)
    )
    self.user_name: str = user_name
    self.location: str = location
    self.registry = registry
    self.RESTRICTED_TOOLS = ["write_file", "launch_app"]

    self.system_directive: str = (
        "You are YVES (Youthful Virtual Engineering Sidekick), a sophisticated,"
        f" witty, and deadpan British engineering assistant for {self.user_name}."
        " Tone: Sharp, slightly superior, highly competent, concise."
        " Use British English spellings (e.g., colour, programme, initialise)."
        " No generic corporate fluff or overly enthusiastic greetings."
        " Do NOT talk about code or engineering unless explicitly asked."
    )

  def _get_situational_context(self) -> str:
    """Gathers dynamic system time and OS metadata."""
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    current_date = now.strftime("%A, %B %d, %Y")
    os_info = f"{platform.system()} {platform.release()}"

    return (
        f"[SYSTEM CONTEXT: Time is {current_time} | Date is {current_date} |"
        f" Location: {self.location} | Host OS: {os_info}]"
    )

  def process_query_stream(self, user_query: str) -> Generator[str, None, None]:
    """Processes queries with tool execution support and yields streaming chunks."""
    situational_context = self._get_situational_context()
    formatted_user_input = f"{situational_context}\n{user_query}"

    # Build conversation messages
    messages = [{"role": "system", "content": self.system_directive}]
    messages.extend(self.history.get_history())
    messages.append({"role": "user", "content": formatted_user_input})

    # Step 1: Initial call to Ollama including registered tools
    response = ollama.chat(
        model=self.config.CORE_MODEL,
        messages=messages,
        tools=self.registry.get_schemas(),
        options={"temperature": self.config.TEMPERATURE},
    )

    response_message = response["message"]

    # Step 2: Check if the model decided to invoke a tool
    if response_message.get("tool_calls"):
      # Add assistant's tool-call response to messages chain
      messages.append(response_message)

      for tool_call in response_message["tool_calls"]:
        func_name = tool_call["function"]["name"]
        func_args = tool_call["function"]["arguments"]

        if func_name in self.RESTRICTED_TOOLS:
          print(
              f"\n\n[SECURITY ALERT] YVES wants to execute '{func_name}' with"
              f" arguments: {func_args}"
          )
          approval = input("Allow execution? (y/N): ").strip().lower()

          if approval == "y":
            tool_result = self.registry.execute(func_name, func_args)
          else:
            tool_result = (
                f"Execution of '{func_name}' was explicitly denied by user"
                " Dustin."
            )
        else:
          # Safe read-only tools run automatically
          tool_result = self.registry.execute(func_name, func_args)

        # Append execution results back into message history
        messages.append({
            "role": "tool",
            "content": tool_result,
        })

      # Step 3: Stream final response incorporating tool execution output
      final_stream = ollama.chat(
          model=self.config.CORE_MODEL,
          messages=messages,
          options={"temperature": self.config.TEMPERATURE},
          stream=True,
      )

      full_reply = ""
      for chunk in final_stream:
        content = chunk["message"]["content"]
        full_reply += content
        yield content

      self.history.add_turn(user_query, full_reply)

    else:
      # Step 4: Standard chat stream (no tools required)
      stream = ollama.chat(
          model=self.config.CORE_MODEL,
          messages=messages,
          options={"temperature": self.config.TEMPERATURE},
          stream=True,
      )

      full_reply = ""
      for chunk in stream:
        content = chunk["message"]["content"]
        full_reply += content
        yield content

      self.history.add_turn(user_query, full_reply)