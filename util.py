# Utility library functions: IO, OS stuff

import sys, string, csv, os, fnmatch, datetime
from subprocess import call

#########################################
# TIME
#########################################

class Timer:
  def __init__(self, total = -1, print_interval = 5):
    # print_interval is in units of seconds
    self.times = [datetime.datetime.now()]
    self.num = 0
    self.print_interval = print_interval
    self.last_print = 0
    self.prev_num = 0
    self.total = int(total)

  def progress_update(self):
    if self.last_print == 0:
      num_secs = (datetime.datetime.now() - self.times[0]).seconds
    else:
      num_secs = (datetime.datetime.now() - self.last_print).seconds

    if num_secs >= self.print_interval:
      self.last_print = datetime.datetime.now()
      print '\n\tTIMER:', self.num, 'iterations at', datetime.datetime.now()
      print '\tTIMER:', self.num - self.prev_num, 'iterations performed in', num_secs, 'seconds'
      print '\t\tRate:', float(self.num - self.prev_num) / num_secs, 'iterations/second'
      
      a = (self.times[1] - self.times[0]) / self.num
      print '\t\t Avg. Iteration Time:', a
      if self.total != -1:
        print '\tTIMER: Total Expected Time for', self.total, \
          'iterations =', a * self.total

      self.prev_num = self.num
    return

  def update(self, print_progress = False):
    if len(self.times) < 2:
      self.times.append(datetime.datetime.now())
    else:
      self.times[-1] = datetime.datetime.now()
    self.num += 1

    if print_progress:
      self.progress_update()
    return



#########################################
# I/O
#########################################
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

#########################################
# OS
#########################################
def ensure_dir_exists(directory):
  # Guarantees that input dir exists
  if not os.path.exists(directory):
    os.makedirs(directory)
  return


def get_fn(string):
  # In: Filename (possibly with directories)
  # Out: Filename without extensions or directories
  return string.split('/')[-1].split('.')[0]


#########################################
# PROJECT STRUCTURE
#########################################

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
