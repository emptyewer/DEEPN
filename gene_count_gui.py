import os
import re
import sys
import glob
import time
import cPickle as pickle
import libraries.joblib.parallel as Parallel

# Custom Functions
import functions.fileio_gui as f
import functions.printio_gui as p
import functions.spinbar as spinbar

input_folder = 'mapped_sam_files'
# Creates the folder that will hold the Genecounts summaries
summary_folder = "gene_count_summary"
# Creates the folder that will hold more granualar data on exon counts per chromosome
chromosomes_folder = "chromosome_files"


main_directory = sys.argv[1]
gene_dictionary = sys.argv[2]
chromosomes_list_name = sys.argv[3]

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        sys.stdout.write('>>> Function %r finished %2.2f sec' % (method.__name__, te-ts))
        sys.stdout.flush()
        return result
    return timed

def get_dictionary(fileName):
    dictionary = pickle.load(open(fileName, 'rb'))
    return dictionary


def make_read_dictionary(SAMfile, chromosomes_list, bin_folder, exonDict):
    totalReads = 0
    iterations = 0
    SAMin = open(SAMfile, 'r')
    readDict = {}
    binoutfile_names = {}

    try:
        if not os.path.exists(bin_folder):
            os.mkdir(bin_folder)
    except IOError:
        pass

    for chrom in chromosomes_list:
        readDict[chrom] = []

    for line in SAMin:
        line.strip()
        split = line.split()
        if line != '\n':
            if not re.match(r'^@', split[0]):
                chromosome = split[2][3:]
                RUmapped = split[2]
                position = int(split[3])
                if RUmapped != '*' and chromosome in exonDict.keys():
                    totalReads += 1
                    iterations += 1
                    readDict[chromosome].append(position)

                if split[2] not in binoutfile_names.keys():#
                    handle = open(os.path.join(bin_folder, split[2] + '.bin'), 'wb')#
                    binoutfile_names[split[2]] = handle#
                binoutfile_names[split[2]].write('%s:%s\n' % (split[3], split[9]))#

    for f in binoutfile_names.keys():
        binoutfile_names[f].close()

    SAMin.close()
    return (readDict, totalReads)


def change_file_name(directory, folder, oldsuffix, newsuffix):
    var = len(oldsuffix)
    for filename in glob.iglob(os.path.join(directory, folder, '*' + oldsuffix)):
        os.rename(filename, filename[:-var] + newsuffix)

def query(chromosome, geneName, Dict, totalReads, output_file, summary_file):
    Ctotal = 0
    Ptotal = 0
    length = 0
    accession = []
    for exonTuple in Dict[chromosome]:
        if exonTuple[4] == geneName:
            counts = Dict[chromosome][exonTuple]
            PPM = counts * float(1000000) / totalReads
            RPKM = PPM * float(1000) / (exonTuple[1] - exonTuple[0])
            output_file.write("\n" + str(exonTuple) + " Counts:" + str(counts) + " PPM:" + str(PPM) + " RPKM:" + str(RPKM))
            Ctotal += counts
            Ptotal += PPM
            length += (exonTuple[1] - exonTuple[0])
            accession = exonTuple[5]
    Rtotal = Ptotal * float(1000) / length        
    output_file.write("\n" + "TOTALS" + "\n" + "Counts:" + str(Ctotal) + " PPM:" + str(Ptotal) + " RPKM:" + str(Rtotal) + " Length:" + str(length) + "\n")
    summary_file.write("\n" + str(chromosome) + " , " + str(geneName) + " , " + str(Ptotal) + ',' + ','.join([x for x
                       in accession]))
    return Rtotal


def allToFile(directory, Dictionary, totalReads, totalReads2, f, sumfolder, chromfolder):
    v = totalReads
    vv = totalReads2
    summaryFile = open(os.path.join(directory, sumfolder, f + '.summaryTEMP.txt'), 'w')
    summaryFile.write(str(f)+","+str(f)+","+str(f)+","+str(f))
    summaryFile.write("\n , TotalReads , " + str(v))
    summaryFile.write("\n , TotalReads (PPM), " + str(vv))
    summaryFile.write("\nChromosome , GeneName , PPM , NCBI_Acc")
    outFile = open(os.path.join(directory, chromfolder, f + '.chromoutputTEMP.txt'), 'w')
    for chrom in Dictionary:
        geneList = []
        for exon in Dictionary[chrom]:
            if exon[4] not in geneList:
                geneList.append(exon[4])
                query(chrom, exon[4], Dictionary, totalReads2, outFile, summaryFile)
    outFile.close()
    summaryFile.close()


def letsCount(directory, summary_folder, chromosomes_folder, input_folder, chromosomes_list, filename):
    sys.stdout.write(">>> Started processing file %s" % filename)
    sys.stdout.flush()
    exonDict = get_dictionary(os.path.join('dictionaries', gene_dictionary))
    infile = os.path.join(directory, input_folder, filename)
    gene_count_bin_folder = os.path.join(directory, "gene_count_indices", filename[:-4])
    # bin_folder = ''
    # if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == 'darwin':
    #     bin_folder = os.path.join(directory, input_folder, '.' + filename[:-4])
    # else:
    #     bin_folder = os.path.join(directory, input_folder, filename[:-4])
    (readDict, totalReads) = make_read_dictionary(infile, chromosomes_list, gene_count_bin_folder, exonDict)
    sys.stdout.write(">>> %d Total Reads (%s)" % (totalReads, filename))
    sys.stdout.flush()
    totalReads2 = 0
    for chrom in chromosomes_list:
        if chrom in exonDict.keys():
            readList = sorted(readDict[chrom])
            exonList = sorted(exonDict[chrom].keys())
            for read in readList:
                if len(exonList) > 0 and read < exonList[0][0]:
                    continue
                for exon in exonList:
                    if read >= exon[0] and read <= exon[1]:
                        exonDict[chrom][exon] += 1
                        totalReads2 += 1
                    elif read > exon[1]:
                        exonList.remove(exon)
            sys.stdout.write('>>> Finished Chromosome %s%s for File (%s)' % (chrom[:20], '' if len(chrom) <= 20 else '...',
                                                                             filename))
            sys.stdout.flush()
            time.sleep(1)
    sys.stdout.write('>>> Creating files and cleaning up... ( %s )' % filename)
    sys.stdout.flush()
    allToFile(directory, exonDict, totalReads, totalReads2, filename, summary_folder, chromosomes_folder)
    change_file_name(directory, summary_folder, '.sam.summaryTEMP.txt', '_summary.csv')
    change_file_name(directory, chromosomes_folder, '.sam.chromoutputTEMP.txt', '_ChrGene.csv')

@timeit
def gene_count(directory, summary_folder, chromosomes_folder, input_folder, chromosomes_list, sam_file_list):
    num_cores = Parallel.cpu_count()
    print ">>> Using %d Processor Cores" % (num_cores - 1)
    _spin = spinbar.SpinCursor(msg="Processing mapped .sam files ...", speed=2)
    _spin.start()
    Parallel.Parallel(n_jobs=num_cores-1)(Parallel.delayed(letsCount)(directory, summary_folder, chromosomes_folder,
                                                                      input_folder, chromosomes_list, f) for f in
                                                                      sam_file_list)
    _spin.stop()


def initialize_folders(directory):
    # Creates the folder that will hold the Genecounts summaries
    fileio.create_new_folder(directory, summary_folder)
    # Creates the folder that will hold more granualar data on exon counts per chromosome
    fileio.create_new_folder(directory, chromosomes_folder)
    fileio.create_new_folder(directory, "gene_count_indices")

if __name__ == '__main__':
    # Instantiate Function Objects for Basic Input Output
    printio = p.printio()
    fileio = f.fileio()

    sys.stdout.write("\n*** Running Gene Count Y2H ***\n\n")
    sys.stdout.flush()

    initialize_folders(main_directory)
    # Makes sure proper files are in their place and returns .sam file list
    sam_file_list = fileio.get_sam_filelist(main_directory, input_folder)
    # Gets list of chromosomes from Y2Hreadme.txt file
    chromosomes_list = fileio.get_chromosomes_list(main_directory, chromosomes_list_name, printio)
    gene_count(main_directory, summary_folder, chromosomes_folder, input_folder, chromosomes_list, sam_file_list)
