from Database import Database
from Git import Git
from Notion import Notion
from log import log

class App:

  def __init__(self, repo, notion, database):
    self._database = Database(**database)
    self._git = Git(**repo)
    self._notion = Notion(
      **notion,
      repo = self._git.repo
    )

    self._delay = 10

    signal.signal(signal.SIGTERM, self._at_exit)

  def _handle_updates(self):
    updates = self._git.get_updates(self._database.get_commit())
    if not updates:
      return

    for file in updates:
      if (
        not file.endswith(".txt") or
        not file.startswith("src")
        not self._database.find_page(file)
      ):
        log(f"Ignore file <{file}>")
        continue
      page = self._database.get_page(file)
      new_body_id = self._notion.update_page(
        file,
        page["page_id"],
        page["body_id"]
      )
      self._database.update_page(file, new_body_id)
    
    self._database.update_commit(self._git.get_commit())

  def run(self, args):
    if len(args) == 0:
      log("No command provided")
      return
    command, options = args[0], args[1:]

    match command:
      case "run": self._watch(options)
      case "new": self._create(options)
      case "del": self._delete(options)
      case _: log(f"Unknown command <{command}>")

  def _watch(self, _):
    self._git.download()

    while True:
      try:
        self._handle_updates()
      except Exception as exc:
        log(exc)
      time.sleep(self._delay)
    
  def _create(self, options):
    if len(args) != 3:
      log("Must be two args: <filename> <title> <parent UUID>")
      return
    page_id, body_id = self._notion.add_page(options[1], options[2])
    self._database.add_page(options[0], page_id, body_id)
  
  def _delete(self, options):
    if len(args) == 0:
      log("No filename provided")
      return
    page_id = self._database.get_page(options[0])["page_id"]
    self._database.delete_page(options[0])
    self._notion.delete(page_id)

  def _at_exit(self):
    self._database.close()
