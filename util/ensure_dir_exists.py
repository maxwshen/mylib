# Guarantees that input dir exists

import os

def ensure_dir_exists(directory):
  if not os.path.exists(directory):
    os.makedirs(directory)
  return