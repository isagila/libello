import re
import os
import pathlib

class ParseException(Exception):

  def __init__(self, message):
    self._message = message
  
  def __repr__(self):
    return self._message

class Node:

  def __init__(self, node_type, options, parent):
    self._type = node_type
    self._options = options
    self._parent = parent 
    self._children = []
  
  def add_child(self, node_type, options):
    if (
      self._type == "block" and 
      len(self._children) == 0 and
      node_type != "paragraph"
    ):
      raise ParseException("Block should starts with text")

    new_node = Node(node_type, options, self)
    self._children.append(new_node)
    return new_node
  
  def parent(self):
    return self._parent
  
  def __repr__(self):
    out = f"{self._type}[{self._options}]"
    return out

class Parser:

  def __init__(self):
    self._tree = Node("page", {}, None)
    self._pointer = self._tree
    self._options = {}
    self._filename = ""

    self._block_headers = [
      "th", "pr", "def", "nota", "fig", "eq", "img"
    ]
    self._re_rich_text = re.compile(
      r"(\$.*?\$)|(\[.*?\]\(.*?\))"
    )
  
  def _is_command(self, line):
    return len(line) > 0 and line[0] in [":", ">", "+"]

  def _is_block_start(self, command):
    return any([ command == ":" + i for i in self._block_headers])

  def _is_block_end(self, command):
    return command == ":end"
  
  def _is_list_item(self, command):
    return command == "+"
  
  def _split_command_line(self, line):
    parts = line.split()
    return parts[0], parts[1:]
    
  def _parse_command(self, command, args):
    if self._pointer._type == "paragraph":
      self._pointer = self._pointer.parent()
    
    if self._is_block_start(command):
      if command == ":img":
        image_src = os.path.normpath(os.path.join(
          "images",
          *pathlib.Path(self._filename).parts[1:-1],
          " ".join(args)
        ))
        self._pointer.add_child("image", { "src": image_src })
      else:
        self._pointer = self._pointer.add_child("block", {
          "type": command[1:]
        })
        if command == ":eq":
          self._pointer._options["expression"] = ""

    elif self._is_block_end(command):
      self._pointer = self._pointer.parent()

    elif self._is_list_item(command):
      self._pointer = self._pointer.add_child("list_item", {
        "children": []
      })
      self._parse_line(" ".join(args))
      self._pointer = self._pointer.parent()

    else:
      raise ParseException(f"Unknown command: {command}")

  def _get_spans(self, line):
    found = list(self._re_rich_text.finditer(line))
    found = list(map(lambda x: x.span(), found))
    
    if len(found) ==  0:
      return [(0, len(line))]

    spans = []
    if found[0][0] != 0:
      spans = [(0, found[0][0])]
    spans.append(found[0])

    for i in range(1, len(found)):
      spans.append((found[i - 1][1], found[i][0]))
      spans.append(found[i])
    
    if found[-1][1] != len(line):
      spans.append((found[-1][1], len(line)))

    return spans

  def _parse_text_line(self, line):
    if line == "":
      if self._pointer._type == "paragraph":
        self._pointer = self._pointer.parent()
      return

    if (
      self._pointer._type == "block" and
      self._pointer._options["type"] == "eq"
    ):
      self._pointer._options["expression"] += line
      return

    prefix = " "
    if self._pointer._type != "paragraph":
      self._pointer = self._pointer.add_child("paragraph", {})
      prefix = ""

    self._parse_line(prefix + line)
  
  def _parse_line(self, line):
    for span in self._get_spans(line):
      part = line[span[0]:span[1]]
      if part[0] == "$":
        self._pointer.add_child("katex", {
          "expression": part[1:-1]
        })
      elif part[0] == "[":
        text, href = part[1:-1].split("](")
        self._pointer.add_child("link", {
          "content": text,
          "href": href,
        })
      elif part != "":
        self._pointer.add_child("text", { "content": part })

  def parse_header(self, filename):
    lines = open(filename, "r", encoding="utf8").readlines()
    if len(lines) < 4:
      raise ParseException(f"Unable to parse header in file <{filename}>")

    keys = ["page_id", "title", "cover"]
    result = {}
    for i, key in enumerate(keys):
      result[key] = lines[i][len(key) + 2:].strip()

    return result

  def parse_file(self, filename):
    self._tree = Node("page", {}, None)
    self._pointer = self._tree
    self._options = {}
    self._filename = filename

    lines = open(filename, "r", encoding="utf8").readlines()
    for i, line in enumerate(lines):
      if i < 3: # skip header
        continue
      line = line.strip()

      if self._is_command(line):
        command, args = self._split_command_line(line)
        try:
          self._parse_command(command, args)
        except ParseException as exc:
          raise ParseException(
            f"Failed to parse line {i + 1} at file {filename}" + 
            f" with following error:\n\n {exc}"
          )
      else:
        self._parse_text_line(line)

    return self._tree

  def make_exception(self, message):
    result = Node("page", {}, None)
    block = result.add_child("block", {
      "type": "err"
    })
    paragraph = block.add_child("paragraph", {})
    paragraph.add_child("text", { "content": str(message) })
    return result
