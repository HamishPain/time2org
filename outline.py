
# Uses regex for various string matching
import re
import json
from typing import List, Set

letters = set([x for x in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"])
numberics = set([x for x in "0123456789."])
command_symbols = set([x for x in "#+/*"])

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
  return  text.strip().startswith('//')

#%%
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
    


  print(link_dict)

findLinksInText("Hello this is a [[LINK_ID_123][link][link]]. [[LINK_ID_132][ref]] Find out how to use these [[NODE_ID_124][ref][link]], or test a link by [having [lots [of [recursive, things] in] your] text]")
#%%
command_map = {""}

# Process a line of text. If it's a command, split it up and call the associated function
def process(line: str):
  if line and line != '\n' and not checkLineForComment(line):

    # Command
    if re.search("#\+", line):
      line = line.split()
      command = line[0].replace("#+","")
      line.replace(command, "")
      if "=>" in line:
        input_payload, output_payload, *args = line.split("=>")
        input_obj = processInput(input_payload)
        output_obj = processInput(output_payload)

    # Headings
    elif line.strip().startswith('*'):
      # We have a heading! Check indentation
      indentation = len(charGroup(line, ["*"]))
      return line
    
    # A list
    elif line.strip().startswith("-") or re.search("^[0-9]+$", line.strip()):
      return line

    # Some text! Maybe including links or #tags
    else:
      tag_list = re.findall(r"#(\w+)", line)


  return None

# read a .org text file, split into lines
with open("test.nd", 'r') as f:
  lines = f.readlines()

# go over every line and parse into a data structure
# no nesting is allowed
data_struct = []
line_index = 0

while line_index < len(lines):
  current_line = lines[line_index]
  if checkLineForComment(current_line):
    continue

  # Process a multi-line object
  if re.search('#\+BEGIN_', current_line):
    while not re.search('#\+END_', current_line) or line_index > len(lines):
      if not checkLineForComment(current_line):
        line_index += 1
        current_line+=lines[line_index]

  line_index += 1

  data = process(current_line)
  if data:
    data_struct.append(data)

print(data_struct)

def appendData(command: str, data_obj: object=None, multi_line: bool = False):
  append_str = "#+" +command + ("_BEGIN\n" if multi_line else " ")
  if data_obj:
    append_str += json.dumps(data_obj, indent=2 if multi_line else None)
  append_str += "#+{}_END".format(command) if multi_line else ""

  return append_str

x = {"auto":True,"values":["Hello", "Goodbye", "So long"]}

print(appendData("TRIANGLE", data_obj=x, multi_line=True))
#%%
import json
print(json.dumps([{"property":"value"}], separators=([',',': ']), ensure_ascii=True, ))
# %%
