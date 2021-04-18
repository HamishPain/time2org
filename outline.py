#%%
# Uses regex for various string matching
from typing import List, Set
import time2func as t2
import re
from pprint import pprint
from importlib import reload 

reload(t2)

node = t2.time2node.fromFile("simple_test.nd")
node.update()

#%%

# node.transposeWidgetUp(node.widgets[1])

# for i in node.widgets:
#   print(i.__repr__(), end='')

# node.transposeWidgetUp(node.widgets[2])

# print("---------------------------------------------------------------------------------------------------------")

# for i in node.widgets:
#   print(i.__repr__(), end='')




# for i in node.widgets:
#   print(i.__repr__(), end='')

node.addWidget(t2.DateModifiedPropertyWidget())
node.saveFile()

# %%
