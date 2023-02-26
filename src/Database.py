import os
import sqlite3

class Database:

  def __init__(self, path):
    self._connection = sqlite3.connect(path)
    self._cursor = self._connection.cursor()
  
  def get_commit(self):
    return self._cursor.execute(
      "SELECT hash FROM last_commit WHERE id = 0"
    ).fetchone()[0]
  
  def update_commit(self, new_hash):
    self._cursor.execute(
      "UPDATE last_commit SET hash = ? WHERE id = 0",
      (new_hash, )
    )
    self._connection.commit()

  def get_page(self, filename):
    res = self._cursor.execute(
      "SELECT (page_id, body_id) FROM pages WHERE filename = ?",
      (self._normalize(filename), )
    ).fetchone()

    return {
      "page_id": res[0],
      "body_id": res[1],
    }
    
  def update_page(self, filename, body_id):
    self._cursor.execute(
      "UPDATE pages SET body_id = ? WHERE filename = ?",
      (body_id, self._normalize(filename))
    )
    self._connection.commit()
  
  def close(self):
    self._connection.commit()
    self._connection.close()

  @staticmethod
  def _normalize(path):
    return os.normpath(path)
  