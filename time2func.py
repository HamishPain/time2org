# Uses regex for various string matching
import re
import json
from typing import List, Set, Union

letters = set([x for x in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"])
numberics = set([x for x in "0123456789."])
command_symbols = set([x for x in "#+/*"])

class Widget:
  def __init__(self, widget_text=""):
    self.widget_text = widget_text

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

def processInput(text: str):
  if "{" in text:
    try:
      return json.loads(text)
    except:
      return None
  else:
    # Split into array of tags and dict of things
    property_list = []
    property_dict = {}
    text = text.split()
    for token in text:
      if ':' in token:
        prop, value, *args = token.split()
        property_dict[prop] = value
      else:
        property_list.append(token)
    return [property_list, property_dict]

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

def findLinksInText(text: str):
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
  

# Process a line of text. If it's a command, split it up and call the associated function
def process(line: str) -> List[Union[str, object]]:

  # A comment
  if re.search("^\s*\/\/", line):
    return "comment",line

  # Property
  elif re.search("^\s*#\+[a-zA-Z]*:", line):
    
    command, input_data = line.split(":", maxsplit=1)
    output_data = ""
    if "=>" in input_data:
      input_data, output_data = input_data.split("=>", maxsplit=1)
    

    return "property", command+" input: "+str(input_data.split())+" output: "+str(output_data.split())

  # Multiline function
  elif re.search("^\s*#\+(BEGIN_)[a-zA-Z_]*", line) and re.search("#\+(END_)[a-zA-Z_]*", line):
    print("multiline")
    x = re.search("^\s*#\+(BEGIN_)[a-zA-Z_]*", line)
    y = re.search("#\+(END_)[a-zA-Z_]*", line)
    command = line[x.start():x.end()]
    input_data = line[x.end():y.start()]
    command = command[2:]
    output_data = "{}"
    
    if "=>" in input_data:
      input_data, output_data, *args = input_data.split("=>")
    
    if not '{' in input_data:
      input_data = "{}"
    
    try:
      input_obj = json.loads(input_data)
    except:
      print("Input issue")
      print(input_data)
    try:
      output_obj = json.loads(output_data)
    except:
      print("output issue")
      print(output_data)
    
    return "function",line

  # Function
  elif re.search("^\s*#\+[a-zA-Z_]*", line):
    x = re.search("^\s*#\+[a-zA-Z_]*", line)
    command = line[x.start():x.end()]
    input_data = line[x.end():]
    command = command[2:]
    output_data = "{}"
    
    if "=>" in input_data:
      input_data, output_data, *args = input_data.split("=>")
    
    input_data = input_data if input_data.strip() else "{}"
    
    input_obj = json.loads(input_data)
    output_obj = json.loads(output_data)
    
    return "function",command+" input: "+str(input_obj)+" output: "+str(output_obj)

  # Headings
  elif line.strip().startswith('*'):
    # We have a heading! Check indentation
    indentation = len(charGroup(line, ["*"]))
    return "heading",line
  
  # A list
  elif line.strip().startswith("-") or re.search("^[0-9]+$", line.strip()):
    return "list",line

  # Some text! Maybe including links or #tags
  else:
    tag_list = re.findall(r"#(\w+)", line)
    links = findLinksInText(line)
    return "text",line

  return "unknown",line


def appendData(command: str, data_obj: object=None, multi_line: bool = False):
  append_str = "#+BEGIN_" +command + ("\n" if multi_line else " ") + "=>\n"
  if data_obj:
    append_str += json.dumps(data_obj, indent=2 if multi_line else None)
  append_str += "\n#+END_{}".format(command) if multi_line else ""

  return append_str


class time2node:
  def __init__(self):
    self.widgets = [] #Ordered list of widget objects
    self.save_string = ""
    self.filename = ""
  
  def loadFile(self, filename):
    self.filename = filename

    # read a .org text file, split into lines
    with open(self.filename, 'r') as f:
      lines = f.readlines()

    # go over every line and parse into a data structure
    # no nesting is allowed
    line_index = 0

    while line_index < len(lines):
      current_line = lines[line_index]
      
      # Process a multi-line object
      if re.search('#\+BEGIN_', current_line):
        while not re.search('#\+END_', current_line) or line_index > len(lines):
          if not checkLineForComment(current_line):
            current_line+=lines[line_index]
          line_index += 1

      line_index += 1

      line_type, data = process(current_line)
      if data:
        if len(self.widgets) and self.widgets[-1][0] == "text" and line_type == "text":
          self.widgets[-1][1] += data
        else:
          self.widgets.append([line_type, data])

  #TODO implement save file
  def saveFile(self):
    pass

  @classmethod
  def fromFile(cls, filename):
    node = time2node()
    node.loadFile(filename)
    return node






if __name__=="__main__":
  x = {"auto":True,"values":["Hello", "Goodbye", "So long"]}
  print(appendData("TRIANGLE", data_obj=x, multi_line=True))