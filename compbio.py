import Bio

FASTQ_OFFSET = 33

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

def fasta_generator(fasta_fn):
  head = ''
  with open(fasta_fn) as f:
    for i, line in enumerate(f):
      if line[0] == '>':
        head = line
      else:
        yield [head.strip(), line.strip()]

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