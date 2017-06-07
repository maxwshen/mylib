import Bio, sys, os, subprocess
from collections import defaultdict

FASTQ_OFFSET = 33

#########################################
# Biology 
#########################################

def reverse_complement(dna):
  lib = {'A': 'T', 'G': 'C', 'C': 'G', 'T': 'A', 'N': 'N'}
  return ''.join([lib[s] for s in dna][::-1])

#########################################
# Biology parameters
#########################################

def hg19_chromosome_size(chro):
  # source: https://genome.ucsc.edu/goldenpath/help/hg19.chrom.sizes
  chr_sizes = {'1': 249250621, '2': 243199373, '3': 198022430, '4': 191154276, '5': 180915260, '6': 171115067, '7': 159138663, '8': 146364022, '9': 141213431, '10': 135534747, '11': 135006516, '12': 133851895, '13': 115169878, '14': 107349540, '15': 102531392, '16': 90354753, '17': 81195210, '18': 78077248, '19': 59128983, '20': 63025520, '21': 48129895, '22': 51304566, 'X': 155270560, 'Y': 59373566, 'M': 16571}
  return chr_sizes[chro]

#########################################
# Alignments
#########################################

#########################################
# I/O
#########################################

def get_genomic_seq_twoBitToFa(genome, chro, start, end):
  TOOL = '/cluster/mshen/tools/2bit/twoBitToFa'
  TOOL_DB_FOLD = '/cluster/mshen/tools/2bit/'
  ans = subprocess.check_output(TOOL + ' ' + TOOL_DB_FOLD + genome + '.2bit -noMask stdout -seq=' + chro + ' -start=' + str(start) + ' -end=' + str(end), shell = True)
  ans = ''.join(ans.split('\n')[1:])
  return ans.strip()


def fasta_generator(fasta_fn):
  head = ''
  with open(fasta_fn) as f:
    for i, line in enumerate(f):
      if line[0] == '>':
        head = line
      else:
        yield [head.strip(), line.strip()]

def read_fasta(fasta_fn):
  labels, reads = [], []
  with open(fasta_fn) as f:
    for i, line in enumerate(f):
      if line[0] == '>':
        labels.append(line.replace('>', '').strip())
      else:
        reads.append(line.strip())

  return labels, reads

class NarrowPeak:
  # Reference: 
  # https://genome.ucsc.edu/FAQ/FAQformat.html#format12
  def __init__(self, line):
    words = line.split()
    if len(words) != 10:
      print 'ERROR: Input not in valid NarrowPeak format'

    self.chrom = words[0]
    self.chrom_int = int(self.chrom.replace('chr', ''))
    self.chromstart = int(words[1])
    self.chromend = int(words[2])
    self.name = words[3]
    self.score = float(words[4])
    self.strand = words[5]
    self.signalvalue = float(words[6])
    self.pvalue = float(words[7])
    self.qvalue = float(words[8])
    self.peak = float(words[9])

def read_narrowpeak_file(fn):
  peaks = []
  with open(fn) as f:
    for i, line in enumerate(f):
      peaks.append(NarrowPeak(line))
  print 'Found', len(peaks), 'peaks'
  return peaks


def SeqIO_fastq_qual_string(rx):
  # Takes as input a Bio.SeqIO object
  quals = rx.letter_annotations['phred_quality']
  return ''.join([chr(s + 33) for s in quals])

class RepeatMasker:
  def __init__(self, genome):
    print '\tBuilding Repeats...'
    self.data = defaultdict(list)
    with open('/cluster/mshen/tools/repeatmasker/' + genome + '.repeats.txt') as f:
      for i, line in enumerate(f):
        w = line.split(',')
        self.data[w[0]].append( (int(w[1]), int(w[2])) )

  def trim(self, chro, start, end):
    new_data = defaultdict(list)
    for xk in self.data[chro]:
      if start <= xk[0] < xk[1] <= end:
        new_data[chro].append((xk[0], xk[1]))
    self.data = new_data
    return

  def search(self, chro, start, end):
    cands = self.data[chro]
    for cand in cands:
      if cand[0] < start < cand[1] or cand[0] < end < cand[1]:
        return True
    return False
