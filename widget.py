'''

'''

from node_helper import *
import regex as re
import json
import datetime

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
    self.command = command[8:]

    input_data = widget_text[x.end():y.start()]
    
    if "=>" in input_data:
      input_data, output_data, *args = input_data.split("=>")
    
    try:
      self.input_obj = json.loads(input_data)
    except:
      print("Could not load input object")
      self.input_obj = {}

    try:
      self.output_obj = json.loads(output_data)
    except:
      print("Could not load output object")
      self.output_obj = {}
  
  def __str__(self):
    return "#+BEGIN_{}\n{}\n{}\n{}\n#+END_{}\n".format(self.command, json.dumps(self.input_obj, indent=2), " => ", json.dumps(self.output_obj, indent=2), self.command)

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
  
  def __str__(self):
    return "#+{}: {}{}{}\n".format(self.name, ' '.join(self.input_object) if self.input_object else ""," => " if self.output_object else "", ' '.join(self.output_object) if self.output_object else "")


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

