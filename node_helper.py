import json
from typing import Dict, List, Set
import regex as re
import random
import datetime

letters = [x for x in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"]
numberics = [x for x in "0123456789."]
command_symbols = [x for x in "#+/*"]

def generateNodeID():
  random.seed(datetime.datetime.now().timestamp())
  return ''.join([random.choice(letters[:-1]+numberics[:-1]) for x in range(20)])

def isType(text_type:str, type_list=["text", "heading", "list"]):
  return text_type in type_list

def charGroup(text: str, allowed_chars: List[str] or Set[str]) -> str:
  text = text.strip()
  new_line = ""
  for character in text:
    if character in allowed_chars:
      new_line += character
    else:
      break
  return new_line

# def processInput(text: str):
#   if "{" in text:
#     try:
#       return json.loads(text)
#     except:
#       return None
#   else:
#     # Split into array of tags and dict of things
#     property_list = []
#     property_dict = {}
#     text = text.split()
#     for token in text:
#       if ':' in token:
#         prop, value, *args = token.split()
#         property_dict[prop] = value
#       else:
#         property_list.append(token)
#     return [property_list, property_dict]

def checkLineForComment(text: str):
  return re.search("^\s*\/\/", text) != None

def findBracketedText(text: str):
  stack = []
  base_count = 0
  for i, c in enumerate(text):
      if c == '[':
          stack.append(i)
      elif c == ']' and stack:
          start = stack.pop()
          selected_text = text[start + 1: i]
          if len(stack) == 0:
            yield selected_text
            base_count += 1

def findLinksInText(text: str) -> Dict[str,List[str]]:
  bracket_list = list(findBracketedText(text))
  link_dict = {}
  for text in bracket_list:
    text_split = list(findBracketedText(text))
    node_ID, link_type, description = "","",""
    # Link
    if len(text_split) == 1 and not '[' in text_split[0] and not ']' in text_split[0]:
      node_ID = text_split[0]
    # Link | Type
    elif len(text_split) == 2:
      node_ID, link_type = text_split    
    # Link | Type | Description
    elif len(text_split) == 3:
      node_ID, link_type, description = text_split
    else:
      continue

    if not link_type in link_dict: link_dict[link_type] = []
    link_dict[link_type].append(node_ID)
  return link_dict


def appendData(command: str, data_obj: object=None, multi_line: bool = False):
  append_str = "#+BEGIN_" +command + ("\n" if multi_line else " ") + "=>\n"
  if data_obj:
    append_str += json.dumps(data_obj, indent=2 if multi_line else None)
  append_str += "\n#+END_{}".format(command) if multi_line else ""

  return append_str