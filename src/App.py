from Git import Git
from Notion import Notion
from log import log

import os
import sys
import time

class App:

  def __init__(self, repo, notion):
    self._git = Git(**repo)
    self._notion = Notion(**notion, repo_path = self._git.get_path)
    self._delay = 10
    self._commit_file = os.path.abspath("last_commit.txt")

  def _is_source_file(self, file):
    return file.endswith(".txt") and file.startswith("src")

  def _handle_updates(self):
    updates = self._git.get_updates(self._get_commit())
    if not updates:
      return
    log(f"Found {len(updates)} updates")

    for file in updates:
      if not self._is_source_file(file) or not os.path.exists(file):
        log(f"Ignore file <{file}>")
        continue
      try:
        self._notion.update_page(file)
      except Exception as exc:
        log(exc)
      
    self._update_commit(self._git.get_commit())

  def run(self):
    self._git.download()

    while True:
      try:
        self._handle_updates()
      except Exception as exc:
        log(exc)
      time.sleep(self._delay)

  def _get_commit(self):
    with open(self._commit_file, "r", encoding="utf8") as file:
      return file.read().strip()

  def _update_commit(self, new_commit):
    with open(self._commit_file, "w", encoding="utf8") as file:
      file.write(new_commit)
