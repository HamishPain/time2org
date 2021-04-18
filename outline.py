#%%
# Uses regex for various string matching
from widget import PropertyWidget
from node_helper import findBracketedText, findLinksInText
from typing import List, Set
import time2func as t2
import re
from pprint import pprint
from importlib import reload 

reload(t2)

graph = t2.time2graph()
graph.load()

for node in graph.nodes:
  print(node.nicknames)

nodes = graph.findNodes(nicknames=["simple"])
if nodes:
  print(nodes)
  node = nodes[0]
  node.addWidget(t2.DateModifiedPropertyWidget())
  node.saveFile()

node = graph.spawnNode()
node.addWidget(PropertyWidget("#+TITLE: test_2"))
node.update()
graph.save()

# %%

t = "[[NODE_ID]]\n[[Welcome][parent]] [[Test2][seven][A place that we all know and love]]"
print(findLinksInText(t))