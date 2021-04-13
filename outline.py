#%%
# Uses regex for various string matching
from typing import List, Set
import time2func as t2
import re
from pprint import pprint
from importlib import reload 

reload(t2)

node = t2.time2node.fromFile("test.nd")
node.update()
#%%
for i in node.widgets:
  print(i.__repr__(), end='')

# %%
