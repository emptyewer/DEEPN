class process():

    def __init__(self):
        self.codonTable = {"TTT" : "F", "TTC" : "F", "TTA" : "L", "TTG" : "L",
                   "TCT"  : "S", "TCC"  : "S", "TCA"  : "S", "TCG"  : "S",
                   "TAT"  : "Y", "TAC"  : "Y", "TAA"  : ".", "TAG"  : ".",
                   "TGT"  : "C", "TGC"  : "C", "TGA"  : ".", "TGG"  : "W",
                   "CTT"  : "L", "CTC"  : "L", "CTA"  : "L", "CTG"  : "L",
                   "CCT"  : "P", "CCC"  : "P", "CCA"  : "P", "CCG"  : "P",
                   "CAT"  : "H", "CAC"  : "H", "CAA"  : "Q", "CAG"  : "Q",
                   "CGT"  : "R", "CGC"  : "R", "CGA"  : "R", "CGG"  : "R",
                   "ATT"  : "I", "ATC"  : "I", "ATA"  : "I", "ATG"  : "M",
                   "ACT"  : "T", "ACC"  : "T", "ACA"  : "T", "ACG"  : "T",
                   "AAT"  : "N", "AAC"  : "N", "AAA"  : "K", "AAG"  : "K",
                   "AGT"  : "S", "AGC"  : "S", "AGA"  : "R", "AGG"  : "R",
                   "GTT"  : "V", "GTC"  : "V", "GTA"  : "V", "GTG"  : "V",
                   "GCT"  : "A", "GCC"  : "A", "GCA"  : "A", "GCG"  : "A",
                   "GAT"  : "D", "GAC"  : "D", "GAA"  : "E", "GAG"  : "E",
                   "GGT"  : "G", "GGC"  : "G", "GGA"  : "G", "GGG"  : "G",}

        self.base_complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
    
    def translate_orf(self, ORF):
        protein_sequence = ""
        try:
            for codon in range(0, (len(ORF)-1),3):
                amino_acid = self.codonTable[ORF[codon:codon+3]]
                protein_sequence = protein_sequence + amino_acid           
            return protein_sequence
        except KeyError:
            return protein_sequence

    def _complement(self, s): 
        letters = list(s) 
        letters = [self.base_complement[base] for base in letters]
        return ''.join(letters)

    def reverse_complement(self, s):
        return self._complement(s[::-1])

    # def _get_sequence(self, accNumber):
    #     mRNAinfile = open(os.path.join(os.curdir, 'Resources', 'mm10GeneList.txt'), 'r')
    #     for line in mRNAinfile:
    #         line.strip()
    #         splitLine2 = line.split()
    #         NMnumber = splitLine2[0]
    #         geneName = splitLine2[1]
    #         Chromosome = splitLine2[2]
    #         CHRstart = splitLine2[4]
    #         CHRstop = splitLine2[5]
    #         ORFstart = splitLine2[6]
    #         ORFstop = splitLine2[7]
    #         sequencelow = splitLine2[8]
    #         if NMnumber == accNumber:
    #             break
    #     sequence = sequencelow.upper()
    #     mRNAinfile.close()
    #     return NMnumber, geneName, Chromosome, CHRstart, CHRstop, sequence, ORFstart, ORFstop
    #
    # def make_mRNA_list(self, accNumber):
    #     _, _, _, _, _, sequence, ORFstart, ORFstop = self._get_sequence(accNumber)
    #     sequence.upper()
    #     listlength = int((len(sequence)-25)/int(interval))
    #     print len(sequence), ': Length of mRNA'
    #     seqs = []
    #     count = 0
    #     position = 0
    #     while count <= listlength and position <= len(sequence):
    #         sequencepart = sequence[position:position + 20]
    #         seqs.append(sequencepart)
    #         count += 1
    #         position += interval
    #     return (seqs, ORFstart, ORFstop)
    #
    # def make_listofreads(self, accNumber, NAMEofFILE):
    #     infile= open(os.path.join(os.curdir, placeofmappedsamfiles, NAMEofFILE), 'r')
    #     NMnumber, geneName, Chromosome, CHRstart, CHRstop, _, _, _ = self._get_sequence(accNumber)
    #     counts=0
    #     listofreads=[]
    #     for line2 in infile:
    #         line2.strip()
    #         splitLine = line2.split()
    #         countlist=[]
    #         if splitLine[0][0] != '@'and splitLine[2] == Chromosome and splitLine[3] >= CHRstart and splitLine[3] <= CHRstop:
    #             listofreads.append(splitLine[9])
    #             counts += 1
    #     infile.close()
    #     return(listofreads, geneName)

