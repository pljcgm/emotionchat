from docopt import docopt
from src.client import Client
import tkinter

__doc__ = \
    """
EmotionChat CLI.

Usage:
  emotionchat.py [--host=<hostip>] [--model=<modelfile>]
  emotionchat.py -h | --help

Options:
  -h --help             Show this screen.
  --host=<hostip>       IP/DNS of Server [default: 'lucasjeske.de'].
  --model=<modelfile>   Model to be used [default: 'model_self_trained.h5'].
"""

if __name__ == "__main__":
    arguments = docopt(__doc__, version="0.1b")
    host = 'lucasjeske.de'
    model = 'model_self_trained.h5'
    if arguments["--list"]:
        host = arguments["<hostip>"]
    if arguments["--model"]:
        model = arguments["<modelfile>"]

    root = tkinter.Tk()
    client = Client(root, host, model)
    root.mainloop()
