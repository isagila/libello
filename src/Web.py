import requests

class Web:

  def __init__(self, headers = {}, prefix = ""):
    self._prefix = prefix
    self._headers = headers

  def get(self, url):
    return requests.get(
      self._prefix + url,
      headers = self._headers
    ).json()

  def post(self, url, options):
    return requests.post(
      self._prefix + url,
      headers = self._headers,
      json = options
    ).json()

  def patch(self, url, options):
    return requests.patch(
      self._prefix + url,
      headers = self._headers,
      json = options
    ).json()

  def delete(self, url):
    return requests.delete(
      self._prefix + url,
      headers = self._headers
    ).json()
