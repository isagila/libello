import sys
import json

from App import App

def main():
  with open(sys.argv[1], "r", encoding="utf8") as file:
    settings = json.loads(file.read())
  App(**settings).run()

if __name__ == "__main__":
  main()
