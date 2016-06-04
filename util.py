# Utility library functions: IO, OS stuff

import sys, string, csv, os, fnmatch
from subprocess import call


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


def get_prev_step(f, src_dir):
  # Assumes a folder of python functions
  #   utility files like _runall, _clean start with _
  #   processing steps begin with a_, b_, ...
  # Given a step file, returns the previous step filename

  steps = [x.replace('.py', '') for x in os.listdir(src_dir) if fnmatch.fnmatch(x, '?*_*.py')]
  sorted(steps)
  name = get_fn(f)
  ind = steps.index(name)
  if ind > 0:
    return steps[ind - 1]
  else:
    print 'Error: No previous step for first script', f
  return ''

def cp_config_to_results(src_dir, results_place):
  call(['cp', src_dir + '_config.py', results_place])
  return

def code_dependency(src_dir):
  # Returns the input/output dependency of a collection of 
  # python scripts
  #
  # Looks for the variable DEFAULT_INP_DIR 

  dep = dict()

  for fn in os.listdir(src_dir):
    if fnmatch.fnmatch(fn, '*.py'):
      with open(src_dir + fn) as f:
        for i, line in enumerate(f):
          words = line.split()
          if len(words) > 0 and words[0] == 'DEFAULT_INP_DIR':
            inp = ' '.join(words[2:])
            dep[fn] = inp
  with open(src_dir + '_dependencies.txt', 'w') as f:
    f.write('Script Name: Expected input folder\n\n')
    for k in sorted(dep.keys()):
      f.write(k + ': ' + dep[k] + '\n')
  return
