# Reads in a text file with the given delimiter, like '\t'

import csv

def read_delimited_txt(inp_fn, dlm):
  print 'Reading in', inp_fn, '...'
  with open(inp_fn) as f:
    reader = csv.reader(f, delimiter = dlm)
    d = list(reader)
  return d