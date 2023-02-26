from Process import Process

import os

class Git:

  def __init__(self, url, branch, folder = "__source__"):
    self._url = f"https://github.com/{url}.git"
    self._folder = folder
    self._branch = branch
  
  def download(self):
    Process.execute(f"rm -rf {self._folder}")
    Process.execute(f"git clone {self._url} {self._folder}")
    os.chdir(self._folder)
  
  def get_updates(self, commit):
    Process.execute("git pull")
    updates = Process.execute(
      f"git diff {commit} {self._branch} --name-status"
    ).split("\n")[:-1]

    for i, text in enumerate(updates):
      updates[i] = text.split("\t")[1]
    return updates

  def get_commit(self):
    return Process.execute("git log -1 --format=%H").strip()

  @property
  def repo(self):
    return f"{self._url[:-4]}/blob/{self._branch}"
