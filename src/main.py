import argv
import json

from App import App

def main():
  with open("settings.json", "r", encoding="utf8") as file:
    settings = json.loads(file.read())
  App(settings).run(sys.argv[1:])

if __name__ == "__main__":
  main()
