import Bio, sys, os, subprocess
from collections import defaultdict

FASTQ_OFFSET = 33

#########################################
# Biology 
#########################################

def reverse_complement(dna):
  lib = {'A': 'T', 'G': 'C', 'C': 'G', 'T': 'A', 'N': 'N', 'W': 'W', 'S': 'S', 'M': 'K', 'K': 'M', 'R': 'Y', 'Y': 'R'}
  new_dna = ''
  dna = dna.upper()
  for c in dna:
    if c in lib:
      new_dna += lib[c]
    else:
      new_dna += c
  new_dna = new_dna[::-1]
  return new_dna

#########################################
# Biology parameters
#########################################

def hg19_chromosome_size(chro):
  # source: https://genome.ucsc.edu/goldenpath/help/hg19.chrom.sizes
  chr_sizes = {'1': 249250621, '2': 243199373, '3': 198022430, '4': 191154276, '5': 180915260, '6': 171115067, '7': 159138663, '8': 146364022, '9': 141213431, '10': 135534747, '11': 135006516, '12': 133851895, '13': 115169878, '14': 107349540, '15': 102531392, '16': 90354753, '17': 81195210, '18': 78077248, '19': 59128983, '20': 63025520, '21': 48129895, '22': 51304566, 'X': 155270560, 'Y': 59373566, 'M': 16571}
  return chr_sizes[chro]

aa_to_dna_dict = {
  'Ala': ['GCT', 'GCC', 'GCA', 'GCG'],
  'Leu': ['TTA', 'TTG', 'CTT', 'CTC', 'CTA', 'CTG'],
  'Arg': ['CGT', 'CGC', 'CGA', 'CGG', 'AGA', 'AGG'],
  'Lys': ['AAA', 'AAG'],
  'Asn': ['AAT', 'AAC'], 
  'Met': ['ATG'],
  'Asp': ['GAT', 'GAC'], 
  'Phe': ['TTT', 'TTC'],
  'Cys': ['TGT', 'TGC'],
  'Pro': ['CCT', 'CCC', 'CCA', 'CCG'],
  'Gln': ['CAA', 'CAG'],
  'Ser': ['TCT', 'TCC', 'TCA', 'TCG', 'AGT', 'AGC'],
  'Glu': ['GAA', 'GAG'],
  'Thr': ['ACT', 'ACC', 'ACA', 'ACG'],
  'Gly': ['GGT', 'GGC', 'GGA', 'GGG'],
  'Trp': ['TGG'],
  'His': ['CAT', 'CAC'], 
  'Tyr': ['TAT', 'TAC'],
  'Ile': ['ATT', 'ATC', 'ATA'],
  'Val': ['GTT', 'GTC', 'GTA', 'GTG'],
  'Stop': ['TAA', 'TGA', 'TAG'],
}
def dna_to_aa(codon):
  codon = codon.upper()
  for aa in aa_to_dna_dict:
    if codon in aa_to_dna_dict[aa]:
      return aa
  return None

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
        labels.append(line.strip())
      else:
        reads.append(line.strip())
  assert len(labels) == len(reads), 'Imbalanced number of headers/reads'
  return labels, reads

class HgCodingGenes():
  def __init__(self, hg_build):
    self.genome_build = hg_build
    gene_lines = open('/cluster/mshen/mylib/%s_knownGene.txt' % (hg_build)).readlines()
    self.DataBase = defaultdict(dict)
    self.kgXref = None

    if hg_build == 'hg38':
      attr_lines = open('/cluster/mshen/mylib/%s_knownAttrs.txt' % (hg_build)).readlines()
    else:
      attr_lines = None

    for idx, gene_line in enumerate(gene_lines):
      if hg_build == 'hg38':
        attr_line = attr_lines[idx]
        gene_type = attr_line.split()[-1]
        if gene_type != 'coding':
          continue
      elif hg_build == 'hg19':
        pass

      w = gene_line.split('\t')
      name = w[0]
      chrom = w[1]
      strand = w[2]
      codingStart = int(w[5])
      codingEnd = int(w[6])
      exonStarts = [int(s) for s in w[8].split(',')[:-1]]
      exonEnds = [int(s) for s in w[9].split(',')[:-1]]

      # Adjust for UTR
      exonStarts[0] = codingStart
      exonEnds[-1] = codingEnd  

      # Verified properties: exonStart < exonEnd, always
      self.DataBase[chrom][name] = dict()
      self.DataBase[chrom][name]['StartEnd'] = (codingStart, codingEnd)
      self.DataBase[chrom][name]['Exons'] = zip(exonStarts, exonEnds)
      self.DataBase[chrom][name]['Strand'] = strand

  def build_kgXref(self):
    # Database that links kgID (uc062ewk.1) to common gene names (A4GALT).
    # Generally many kgIDs for a single gene name.
    self.kgXref = defaultdict(list)
    with open('/cluster/mshen/mylib/%s_kgXref.txt' % (self.genome_build)) as f:
      for i, line in enumerate(f):
        w = line.split()
        kgid = w[0]
        gene_nm = w[4]
        self.kgXref[gene_nm].append(kgid)
    return

  def get_reading_frame(self, genome, chrom, position, gene_suggestion = None):
    if genome != self.genome_build:
      print 'Error: %s did not match genome build %s' % (genome, self.genome_build)
      return

    if gene_suggestion is not None and self.kgXref is None:
      self.build_kgXref()

    found = []

    for gene in self.DataBase[chrom]:
      coding_start, coding_end = self.DataBase[chrom][gene]['StartEnd']
      strand = self.DataBase[chrom][gene]['Strand']

      if coding_start <= position <= coding_end:
        coding_position = 0
        total_tx_len = sum([e-s for e, s in self.DataBase[chrom][gene]['Exons']])
        for (exonStart, exonEnd) in self.DataBase[chrom][gene]['Exons']:

          if strand == '+':
            in_exon = bool(exonStart <= position < exonEnd)
          else:
            in_exon = bool(exonStart < position <= exonEnd)
          
          if in_exon:
            position_within = position - exonStart

            if strand == '+':
              found_frame = (coding_position + position_within) % 3
            else:
              found_frame = (total_tx_len - coding_position - position_within) % 3
            found.append((found_frame, strand, position - exonStart, position - exonEnd, gene))

          exon_length = exonEnd - exonStart
          coding_position += exon_length

    if len(found) == 1:
      return 'One hit found', found[0]

    elif len(found) > 1:
      if gene_suggestion is None:
        return 'Multiple hits found', found
      else:
        if gene_suggestion in self.kgXref:
          for f in found:
            kgid = f[-1]
            if kgid in self.kgXref[gene_suggestion]:
              return 'One hit found', f
        return 'Multiple hits found', found
    else:
      return 'No hits found', None


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
