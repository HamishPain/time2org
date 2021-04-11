#%%
# Uses regex for various string matching
from typing import List, Set
import time2func as t2
import re
from pprint import pprint
from importlib import reload 

reload(t2)

node = t2.time2node.fromFile("test.nd")

#%%
pprint(node.widgets)

#%%


text = "".join([data for data_type, data in node.widgets if t2.isType(data_type)])
print(text)

#%%
properties = "\n".join([data for data_type, data in node.widgets if t2.isType(data_type, type_list=["property"])])
print(properties)

#%%
functions = "\n".join([data for data_type, data in node.widgets if t2.isType(data_type, type_list=["function"])])
print(functions)