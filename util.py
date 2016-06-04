# Utility library functions: IO, OS stuff

import sys, string, csv, os, fnmatch


def read_delimited_text(inp_fn, dlm, verbose = False):
  # Reads in a text file with the given delimiter, like '\t'
  if verbose:
    print 'Reading in', inp_fn, '...'
  with open(inp_fn) as f:
    reader = csv.reader(f, delimiter = dlm)
    d = list(reader)
  return d

def write_delimited_text(out_fn, lists, dlm):
  # Assumes input as a 2D list, with lines / words
  with open(out_fn, 'w') as f:
    writ = csv.writer(f, delimiter = dlm)
    for line in lists:
      writ.writerow(line)
  return


def ensure_dir_exists(directory):
  # Guarantees that input dir exists
  if not os.path.exists(directory):
    os.makedirs(directory)
  return


def get_fn(string):
  # In: Filename (possibly with directories)
  # Out: Filename without extensions or directories
  return string.split('/')[-1].split('.')[0]


def get_prev_step(f):
  # Assumes a folder of python functions
  #   utility files like _runall, _clean start with _
  #   processing steps begin with a_, b_, ...
  # Given a step file, returns the previous step filename

  d = get_script_dir(f)
  steps = [x.replace('.py', '') for x in os.listdir(d) if fnmatch.fnmatch(x, '?*_*.py')]
  sorted(steps)
  name = get_fn(f)
  ind = steps.index(name)
  if ind > 0:
    return steps[ind - 1]
  else:
    print 'Error: No previous step for first script', f
  return ''

def get_script_dir(f):
  # Returns the directory of the current script
  # Expects __file__ to be passed as f
  return os.path.dirname(os.path.abspath(f))
