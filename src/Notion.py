from Parser import (
  ParseException,
  Node,
  Parser
)
from Web import Web
  
class Notion:

  def __init__(self, api_key, repo_path):
    self._web = Web(
      prefix = f"https://api.notion.com/v1/",
      headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
      }
    )
    self._parser = Parser()
    self._repo_path = repo_path

  def update_page(self, filename, page_id):
    header = self._parser.parse_header(filename)
    page_id = header["page_id"]
    body_id = self._extract_body_id(page_id)

    if body_id:
      self._web.delete(f"blocks/{body_id}")
    try:
      parse_tree = self._parser.parse_file(filename)
    except ParseException as exc:
      parse_tree = self._parser.make_exception(str(exc))

    self._web.patch(
      f"blocks/{page_id}/children", {
        "children": [{
          "type": "synced_block",
          "synced_block": {
            "synced_from": None,
            "children": self._to_dict(parse_tree)
          }
        }]
      }
    )
    self._web.patch(
      f"pages/{page_id}", {
        "icon": {
          "type": "external",
          "external": {
            # TODO: add image support (not only embedded notion icons)
            "url": f"https://www.notion.so/icons/{header['icon']}.svg" 
          }
        },
        # TODO: deal with image path
        # "cover": {
        #   "type": "external",
        #   "external": {
        #     "url": 
        #   }
        # },
        "properties": {
          "title": {
            "title": [
              {
                "type": "text",
                "text": {
                  "content": header["title"]
                }
              }
            ]
          }
        },
      }
    )
  
  def _extract_body_id(self, page_id):
    children = self._web.get(f"blocks/{page_id}/children")["results"]
    if len(children) > 0:
      return children[0]["id"]
    return None

################################################################################

  def _get_image_url(self, path):
    path = path.replace('\\', '/')
    return f"{self._repo}/{path}?raw=true"

  def _get_callout_style(self, stylename):
    icons = {
      "def": "bookmark_pink",
      "th": "fire_green",
      "nota": "warning_orange",
      "pr": "checkmark_blue",
      "fig": "photo-landscape_brown",
      "err": "warning_orange" # TODO
    }
    return {
      "icon": {
        "type": "external",
        "external": {
          "url": f"https://www.notion.so/icons/{icons[stylename]}.svg"
        }
      },
      "color": "default",
    }

  def _page_to_dict(self, node, children):
    return children
  
  def _equation_to_dict(self, node, children):
    return {
      "type": "equation",
      "equation": {
        "expression": node._options["expression"]
      }
    }

  def _block_to_dict(self, node, children):
    if node._options["type"] == "eq":
      return self._equation_to_dict(node, children)

    return {
      "type": "callout",
      "callout": {
        "rich_text": children[0]["paragraph"]["rich_text"],
        "children": children[1:],
        **self._get_callout_style(node._options["type"])
      }
    }
  
  def _paragraph_to_dict(self, node, children):
    return {
      "type": "paragraph",
      "paragraph": {
        "rich_text": children
      }
    }
  
  def _image_to_dict(self, node, children):
    return {
      "type": "image",
      "image": {
        "type": "external",
        "external": {
          "url": self._get_image_url(node._options["src"])
        }
      }
    }

  def _text_to_dict(self, node, children):
    return {
      "type": "text",
      "text": {
        "content": node._options["content"],
        "link": None
      }
    }
  
  def _link_to_dict(self, node, children):
    return {
      "type": "text",
      "text": {
        "content": node._options["content"],
        "link": {
          "url": node._options["href"]
        }
      },
      "href": node._options["href"]
    }

  def _katex_to_dict(self, node, children):
    return {
      "type": "equation",
      "equation": {
        "expression": node._options["expression"],
      }
    }

  def _list_item_to_dict(self, node, children):
    return {
      "type": "bulleted_list_item",
      "bulleted_list_item": {
        "rich_text": children
      }
    }
  
  def _unknown_to_dict(self, node, children):
    return {
      "type": "text",
      "text": {
        "content": f"Unknown node <{node._type}> with {len(children)} children",
        "link": None
      }
    }

  def _to_dict(self, node):
    children = [self._to_dict(child) for child in node._children]

    match node._type:
      case "page":      return self._page_to_dict(node, children)
      case "block":     return self._block_to_dict(node, children)
      case "paragraph": return self._paragraph_to_dict(node, children)
      case "image":     return self._image_to_dict(node, children)
      case "text":      return self._text_to_dict(node, children)
      case "link":      return self._link_to_dict(node, children)
      case "katex":     return self._katex_to_dict(node, children)
      case "list_item": return self._list_item_to_dict(node, children)
    return self._unknown_to_dict(node, children)
