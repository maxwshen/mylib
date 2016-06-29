import Bio

FASTQ_OFFSET = 33

#########################################
# Biology parameters
#########################################

def human_chromosome_size(chro):
  # hg38
  chr_sizes = {'1': 248956422, '2': 242193529, '3': 198295559, '4': 190214555, '5': 181538259, '6': 170805979, '7': 159345973, '8': 145138636, '9': 138394717, '10': 133797422, '11': 135086622, '12': 133275309, '13': 114364328, '14': 107043718, '15': 101991189, '16': 90338345, '17': 83257441, '18': 80373285, '19': 58617616, '20': 64444167, '21': 46709983, '22': 50818468, 'X': 156040895, 'Y': 57227415}
  return chr_sizes[chro]

#########################################
# Alignments
#########################################

#########################################
# I/O
#########################################

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