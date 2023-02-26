from Database import Database
from Git import Git
from Notion import Notion
from log import log

import time
import signal

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
      page = self._database.get_page(file)
      if (
        not file.endswith(".txt") or
        not file.startswith("src") or
        not page
      ):
        log(f"Ignore file <{file}>")
        continue
      new_body_id = self._notion.update_page(
        file,
        page["page_id"],
        page["body_id"]
      )
      self._database.update_page(file, new_body_id)
    
    self._database.update_commit(self._git.get_commit())

  def run(self):
    self._git.download()

    while True:
      try:
        self._handle_updates()
      except Exception as exc:
        log(exc)
      time.sleep(self._delay)

  def _at_exit(self):
    self._database.close()
