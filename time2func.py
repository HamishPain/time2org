# Uses regex for various string matching
from os import link
import re
import json, jsonpickle
from typing import List, Set, Text, Union
import datetime
import random

letters = set([x for x in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"])
numberics = set([x for x in "0123456789."])
command_symbols = set([x for x in "#+/*"])

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
  return link_dict

class Widget:
  
  def __init__(self, widget_text=""):
    self.widget_text = widget_text
    self.input_object = {}
    self.output_object = {}
    self.parseString(widget_text)

  def parseString(self, widget_text:str):
    pass

  match_text = ""

  @classmethod
  def isWidget(cls, line):
    return re.search(cls.match_text, line)
  
  def __repr__(self):
    return self.__class__.__name__ + " " + self.widget_text
  
  def __str__(self):
    return self.widget_text
  
  def reset(self):
    pass

  def updateInternal(self):
    pass

  def updateExternal(self, parent_node):
    pass


class TextWidget(Widget):
  def __init__(self, widget_text):
      self.tag_list = []
      self.links = []
      super().__init__(widget_text=widget_text)
      
  def parseString(self, widget_text: str):  
    self.tag_list += re.findall(r"#(\w+)", widget_text)
    self.links += findLinksInText(widget_text)
  
  def concat(self, widget: Widget):
    self.widget_text += widget.widget_text
    self.parseString(widget.widget_text)


class CommentWidget(TextWidget):
  match_text = "^\s*\/\/"

class FunctionWidget(Widget):
  match_text = "^\s*#\+[a-zA-Z_]*"
  def __init__(self, widget_text):
      super().__init__(widget_text=widget_text)

  def parseString(self, widget_text: str):
      line = widget_text
      x = re.search(self.match_text, line)
      command = line[x.start():x.end()]
      input_data = line[x.end():]
      command = command[2:]
      output_data = "{}"
      
      if "=>" in input_data:
        input_data, output_data, *args = input_data.split("=>")
      
      input_data = input_data if input_data.strip() else "{}"
      
      try:
        self.input_obj = json.loads(input_data)
        self.output_obj = json.loads(output_data)
        return True
      except:        
        return False
  
  def update(self):
    pass

class ClockInWidget(FunctionWidget):
  def __init__(self, widget_text):
      super().__init__(widget_text)

class MultilineFunctionWidget(FunctionWidget):
  @classmethod
  def isWidget(cls, line):
    return re.search("^\s*#\+(BEGIN_)[a-zA-Z_]*", line) and re.search("#\+(END_)[a-zA-Z_]*", line)
  
  def parseString(self, widget_text: str):
    x = re.search("^\s*#\+(BEGIN_)[a-zA-Z_]*", widget_text)
    y = re.search("#\+(END_)[a-zA-Z_]*", widget_text)
    command = widget_text[x.start():x.end()]
    self.command = command[2:]

    input_data = widget_text[x.end():y.start()]
    
    if "=>" in input_data:
      input_data, output_data, *args = input_data.split("=>")
    
    try:
      input_obj = json.loads(input_data)
    except:
      self.input_obj = {}

    try:
      output_obj = json.loads(output_data)
    except:
      self.output_obj = {}

class PropertyWidget(Widget):
  match_text = "^\s*#\+[a-zA-Z]*:"
  
  def parseString(self, widget_text: str):
    try:
      command, input_data = widget_text.split(":", maxsplit=1)
    except:
      command = widget_text.split(":", maxsplit=1)[0]
      input_data = []

    self.name = command[2:]
    output_data = ""
    if "=>" in input_data:
      input_data, output_data = input_data.split("=>", maxsplit=1)
    
    try:
      self.input_object = input_data.split()
    except:
      self.input_object = []
    
    try:
      self.output_object = output_data.split()
    except:
      self.output_object = []
    
    self.widget_text = self.__repr__()
  
  def __repr__(self):
    return "#+"+self.name+": "+str(self.input_object)+"=>"+str(self.output_object)+"\n"

class DateModifiedPropertyWidget(PropertyWidget):
  def parseString(self, widget_text: str):
      super().parseString(widget_text)
      self.name = "DATEMODIFIED"
      if not self.output_object:
        self.output_object = [str(datetime.datetime.now())]


class HeadingWidget(Widget):
  @classmethod
  def isWidget(cls, line):
    return line.strip().startswith('*')
  
  def parseString(self, widget_text: str):
    # We have a heading! Check indentation
    self.indentation = len(charGroup(widget_text, ["*"]))

class ListWidget(Widget):
  @classmethod
  def isWidget(cls, text):
    return text.strip().startswith("-") or re.search("^[0-9]+$", text.strip())



# Process a line of text. If it's a command, split it up and call the associated function
def process(line: str) -> Widget:

  # A comment
  if CommentWidget.isWidget(line):
    return CommentWidget(line)

  # Property
  elif PropertyWidget.isWidget(line):
    return PropertyWidget(line)

  # Multiline function
  elif MultilineFunctionWidget.isWidget(line):
    return MultilineFunctionWidget(line)

  # Function
  elif FunctionWidget.isWidget(line):
    return FunctionWidget(line)

  # Headings
  elif HeadingWidget.isWidget(line):
    return HeadingWidget(line)
  
  # A list
  elif ListWidget.isWidget(line):
    return ListWidget(line)

  # Some text! (or unrecognised garbage) Maybe including links or #tags
  else:
    return TextWidget(line)

  return Widget(line)


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
    self.title = ""
    self.nicknames = []
    self.text = ""
    self.node_ID = ""
  
  def update(self):
    self.text = [widget for widget in self.widgets if widget is TextWidget]
    self.properties = [widget for widget in self.widgets if widget is PropertyWidget]
    self.functions = [widget for widget in self.widgets if widget is FunctionWidget]

    property_widget: PropertyWidget
    for property_widget in self.properties:
      if property_widget.name == 'NICKNAME':
        self.nicknames += property_widget.input_object
      elif property_widget.name == 'TITLE':
        try:
          self.title = property_widget.input_object[0]
        except:
          pass
    
    for function in self.functions:
      pass
    
  
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

      widget = process(current_line)

      if widget:
        if widget is TextWidget and self.widgets and self.widgets[-1] is TextWidget:
          self.widgets[-1].concat(widget)
        else:
          self.widgets.append(widget)

  #TODO implement save file
  def saveFile(self):
    if not self.filename:
      random.seed(datetime.datetime.now().timestamp())
      self.node_ID = self.title+str(random.randint(0,10000000))
    with open(self.filename, 'w') as f:
      widget: Widget
      for widget in self.widgets:
        f.write(widget.__str__())

    pass

  @classmethod
  def fromFile(cls, filename):
    node = time2node()
    node.loadFile(filename)
    return node
  
  def addWidget(self, widget):
    if not widget in self.widgets:
      self.widgets.append(widget)
  
  def transposeWidgetUp(self, widget: Widget):
    index = self.widgets.index(widget)
    if index > 0:
      self.widgets[index-1:index-1] = [widget]
      del self.widgets[index+1]

  
  def transposeWidgetDown(self, widget: Widget):
    index = self.widgets.index(widget)
    if index != -1 and index < len(self.widgets):
      self.widgets[index+1:index+1] = [widget]
      del self.widgets[index]

class time2graph:
  def __init__(self):
    self.nodes = []
    self.node_links = {} # {'NODE_ID':{'Link_type_1':[], 'Link_type_1':[]}}
    self.node_ID = {} #{'NODE_ID':node}
  
  def spawnNode(self):
    node = time2node()
    self.nodes.append(node)

  def add(self, node: time2node):
    self.nodes.append(node)
    self.index(node)
  
  def save(self):


if __name__=="__main__":
  x = {"auto":True,"values":["Hello", "Goodbye", "So long"]}
  print(appendData("TRIANGLE", data_obj=x, multi_line=True))