#%%
# Uses regex for various string matching
from typing import List, Set
import time2func as t2
import re
from pprint import pprint

# read a .org text file, split into lines
with open("test.nd", 'r') as f:
  lines = f.readlines()

# go over every line and parse into a data structure
# no nesting is allowed
data_struct = []
line_index = 0

while line_index < len(lines):
  current_line = lines[line_index]
  
  # Process a multi-line object
  if re.search('#\+BEGIN_', current_line):
    while not re.search('#\+END_', current_line) or line_index > len(lines):
      if not t2.checkLineForComment(current_line):
        current_line+=lines[line_index]
      line_index += 1
  print(current_line)
  line_index += 1

  line_type, data = t2.process(current_line)
  if data:
    if len(data_struct) and data_struct[-1][0] == "text" and line_type == "text":
      data_struct[-1][1] += data
    else:
      data_struct.append([line_type, data])

#%%
pprint(data_struct)

#%%


text = "".join([data for data_type, data in data_struct if t2.isType(data_type)])
print(text)

#%%
properties = "\n".join([data for data_type, data in data_struct if t2.isType(data_type, type_list=["property"])])
print(properties)

#%%
functions = "\n".join([data for data_type, data in data_struct if t2.isType(data_type, type_list=["function"])])
print(functions)
# %%


line = "#+BEGIN_TALLY\n\n#+END_TALLY"
print(re.search("#\+(END_)[a-zA-Z_]*", line))
print(re.search("^\s*#\+(BEGIN_)[a-zA-Z_]*", line))
# %%
