import subprocess

class Process:

  def __init__(self, command, output=None, cwd=None):
    if output is None:
      output = subprocess.DEVNULL

    self._body = subprocess.Popen(
      args = self._make_sudo(command).split(),
      cwd = cwd,
      stdout = output,
      stderr = output
    )
  
  @property
  def id(self):
    return self._body.pid
  
  @property
  def is_alive(self):
    return self._body.poll() is None
  
  def terminate(self):
    if self.is_alive():
      self._body.terminate()

  @staticmethod
  def execute(command, cwd=None):
    return subprocess.check_output(
      args = Process._make_sudo(command).split(),
      cwd = cwd,
      stderr = subprocess.STDOUT
    ).decode("utf8")
  
  @staticmethod
  def _make_sudo(command):
    return f"sudo {command}"
