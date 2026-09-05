import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from yves_config import YvesConfig
from yves_config import HistoryManager
from yves_core import YvesCore


def main():
  config = YvesConfig()
  history = HistoryManager(max_limit=config.MAX_HISTORY)
  yves = YvesCore(config=config, history=history)

  print('=' * 60)
  print(' YVES - Online with Tool Integration')
  print(f" Model: {config.CORE_MODEL} | Type '/clear' to reset, '/exit' to quit")
  print('=' * 60 + '\n')

  while True:
    try:
      user_input = input('Dustin > ').strip()

      if not user_input:
        continue

      if user_input.lower() in ['/exit', 'exit', 'quit']:
        print('\nYVES: Right then. Off I go.')
        break

      if user_input.lower() == '/clear':
        yves.history.clear()
        print('\nYVES: Memory cleared. Fresh slate, then.\n')
        continue

      print('\nYVES: ', end='', flush=True)

      # Stream the response chunks directly to terminal
      for chunk in yves.process_query_stream(user_input):
        print(chunk, end='', flush=True)

      print('\n')

    except KeyboardInterrupt:
      print('\n\nYVES: Session interrupted. Cheerio.')
      break
    except Exception as e:
      print(f'\n[Error]: {e}\n')


if __name__ == '__main__':
  main()