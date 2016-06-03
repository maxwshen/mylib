# Utility library functions: IO, OS stuff

import sys, string, csv, os


def read_delimited_text(inp_fn, dlm):
  # Reads in a text file with the given delimiter, like '\t'

  print 'Reading in', inp_fn, '...'
  with open(inp_fn) as f:
    reader = csv.reader(f, delimiter = dlm)
    d = list(reader)
  return d


def ensure_dir_exists(directory):
  # Guarantees that input dir exists

  if not os.path.exists(directory):
    os.makedirs(directory)
  return