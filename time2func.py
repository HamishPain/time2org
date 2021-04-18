# Uses regex for various string matching
from os import link
import re
import json, jsonpickle
from typing import List, Set, Text, Union
import datetime
import random
from widget import *
from node_helper import *
from pprint import pprint


class time2node:
  def __init__(self):
    self.widgets = [] #Ordered list of widget objects
    self.save_string = ""
    self.filename = ""
    self.title = ""
    self.nicknames: List[str] = []
    self.text: List[TextWidget] = []
    self.properties: List[PropertyWidget] = []
    self.functions: List[FunctionWidget] = []
    self.node_ID = ""
    self.date_created = ""
    self.description = ""
    self.dates_modified: str = []
    self.tags = []
    self.links: Dict[str,List[str]] = {}
    self.backlinks: Dict[str,List[str]] = {}
  
  def update(self):
    self.text: List[TextWidget] = [widget for widget in self.widgets if isinstance(widget, TextWidget)]
    self.properties: List[PropertyWidget] = [widget for widget in self.widgets if isinstance(widget,PropertyWidget)]
    self.functions: List[FunctionWidget] = [widget for widget in self.widgets if isinstance(widget, FunctionWidget)]
    
    self.tags: List[str] = []
    for text_widget in self.text:
      for tag in text_widget.tag_list:
        if tag not in self.tags:
          self.tags += tag
      for link_type, node_ref_list in text_widget.links.items():
        if not link_type in self.links:
          self.links[link_type] = []
        for node_ref in node_ref_list:
          if node_ref not in self.links[link_type]:
            self.links[link_type] += node_ref

    property_widget: PropertyWidget
    for property_widget in self.properties:
      if property_widget.name == 'NICKNAME':
        self.nicknames += property_widget.input_object
      elif property_widget.name == 'TITLE':
        try:
          self.title = property_widget.input_object[0]
        except:
          pass
      elif property_widget.name == 'DESCRIPTION':
        self.description = ' '.join(property_widget.input_object)
      elif property_widget.name == "DATECREATED":
        self.date_created = ''.join(property_widget.input_object)
      elif property_widget.name == "DATEMODIFIED":
        self.dates_modified += property_widget.output_object
    
    for function in self.functions:
      function.updateInternal()

    for function in self.functions:
      function.updateExternal(self)
    
  
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


      widget = processWidget(current_line)

      if widget:
        if isinstance(widget,TextWidget) and self.widgets and isinstance(self.widgets[-1], TextWidget):
          self.widgets[-1].concat(widget)
        else:
          self.widgets.append(widget)

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