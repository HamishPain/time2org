# Uses regex for various string matching
from os import link
import re
import json, jsonpickle
from typing import List, Set, Text, Union
import datetime
import random
from widget import *
from node_helper import *


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
      line_index += 1
      
      # Process a multi-line object
      if re.search('#\+BEGIN_', current_line):
        while not re.search('#\+END_', current_line) and line_index < len(lines):
          if not checkLineForComment(current_line):
            current_line+=lines[line_index]
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
    self.nodes: List[time2node] = []
    self.node_links = {} # {'NODE_ID':{'Link_type_1':[], 'Link_type_1':[]}}
    self.node_ID = {} #{'NODE_ID':node}
  
  def spawnNode(self):
    node = time2node()
    self.nodes.append(node)

  def add(self, node: time2node):
    self.nodes.append(node)
    self.index(node)
  
  def save(self):
    for node in self.nodes:
      node.saveFile()

if __name__=="__main__":
  x = {"auto":True,"values":["Hello", "Goodbye", "So long"]}
  print(appendData("TRIANGLE", data_obj=x, multi_line=True))