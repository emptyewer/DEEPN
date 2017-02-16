import os
import re
import sys
import time
import cPickle as pickle
import libraries.joblib.parallel as Parallel
from libraries.bintrees import AVLTree

# Custom Functions
import functions.fileio_gui as f
import functions.printio_gui as p

input_folder = 'mapped_sam_files'
# Creates the folder that will hold the Genecounts summaries
summary_folder = "gene_count_summary"
# Creates the folder that will hold more granualar data on exon counts per chromosome
chromosomes_folder = "chromosome_files"


main_directory = sys.argv[1]
gene_dictionary = sys.argv[2]
chromosomes_list_name = sys.argv[3]
combined = int(sys.argv[4])

if combined == 1:
    input_folder = 'sam_files'


def get_dictionary(fileName):
    dictionary = pickle.load(open(fileName, 'rb'))
    return dictionary


def make_read_dictionary(sam_file, chromosomes_list, bin_folder, exon_dict):
    total_reads = 0
    iterations = 0
    sam_handle = open(sam_file, 'r')
    read_dict = {}
    binoutfile_names = {}

    try:
        if not os.path.exists(bin_folder):
            os.mkdir(bin_folder)
    except IOError:
        pass

    for chrom in chromosomes_list:
        read_dict[chrom] = []

    for line in sam_handle:
        line.strip()
        split = line.split()
        if line != '\n':
            if not re.match(r'^@', split[0]):
                chromosome = split[2][3:]
                RUmapped = split[2]
                position = int(split[3])
                if RUmapped != '*' and chromosome in exon_dict.keys():
                    total_reads += 1
                    iterations += 1
                    read_dict[chromosome].append(position)

                if split[2] not in binoutfile_names.keys():#
                    handle = open(os.path.join(bin_folder, split[2] + '.bin'), 'wb')#
                    binoutfile_names[split[2]] = handle#
                binoutfile_names[split[2]].write('%s:%s\n' % (split[3], split[9]))#

    for f in binoutfile_names.keys():
        binoutfile_names[f].close()

    sam_handle.close()
    return read_dict, total_reads


def query(chromosome, gene_name, dict, total_reads, output_file, summary_file):
    ctotal = 0
    ptotal = 0
    length = 0
    accession = []
    for exon_tuple in dict[chromosome]:
        if exon_tuple[4] == gene_name:
            counts = dict[chromosome][exon_tuple]
            ppm = 0
            if total_reads > 0:
                ppm = counts * 1000000.0 / total_reads
            rpkm = ppm * 1000.0 / (exon_tuple[1] - exon_tuple[0])
            output_file.write("\n" + str(exon_tuple) + " Counts:" + str(counts) + " PPM:" + str(ppm) + " RPKM:" + str(rpkm))
            ctotal += counts
            ptotal += ppm
            length += exon_tuple[1] - exon_tuple[0]
            accession = exon_tuple[5]
    Rtotal = ptotal * 1000.0 / length
    output_file.write("\n" + "TOTALS" + "\n" + "Counts:" + str(ctotal) + " PPM:" + str(ptotal) + " RPKM:" + str(Rtotal) + " Length:" + str(length) + "\n")
    summary_file.write("\n" + str(chromosome) + " , " + str(gene_name) + " , " + str(ptotal) + ',' + ','.join([x for x
                                                                                                               in accession]))
    return Rtotal


def write_all_to_file(directory, dict, total_reads, total_hits, filename, summary_folder, chromosome_folder):
    summaryFile = open(os.path.join(directory, summary_folder, filename[:-4] + '_summary.csv'), 'w')
    summaryFile.write("File:," + str(filename))
    summaryFile.write("\n , TotalReads , " + str(total_reads))
    summaryFile.write("\n , TotalHits (count), " + str(total_hits))
    summaryFile.write("\nChromosome , GeneName , PPM , NCBI_Acc")
    outFile = open(os.path.join(directory, chromosome_folder, filename[:-4] + '_ChrGene.txt'), 'w')
    for chrom in dict:
        geneList = []
        for exon in dict[chrom]:
            if exon[4] not in geneList:
                geneList.append(exon[4])
                query(chrom, exon[4], dict, total_hits, outFile, summaryFile)
    outFile.close()
    summaryFile.close()


def lets_count(directory, summary_folder, chromosomes_folder, input_folder, chromosomes_list, filename):
    start_time = time.time()
    sys.stdout.write(">>> Started processing file %s\n" % filename)
    sys.stdout.flush()
    exon_dict = get_dictionary(os.path.join('dictionaries', gene_dictionary))
    infile = os.path.join(directory, input_folder, filename)
    gene_count_bin_folder = os.path.join(directory, "gene_count_indices", filename[:-4])
    # bin_folder = ''
    # if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == 'darwin':
    #     bin_folder = os.path.join(directory, input_folder, '.' + filename[:-4])
    # else:
    #     bin_folder = os.path.join(directory, input_folder, filename[:-4])
    (read_dict, total_reads) = make_read_dictionary(infile, chromosomes_list, gene_count_bin_folder, exon_dict)
    sys.stdout.write(">>> %d Total Reads (%s)\n" % (total_reads, filename))
    sys.stdout.flush()
    total_hits = 0
    for chrom in chromosomes_list:
        if chrom in exon_dict.keys():
            read_list = read_dict[chrom]
            exon_dict_list = exon_dict[chrom]

            # Creating KV pairs for AVL tree, start is for beginning of the exon and end is for the last bp of the exon
            kv_start_pairs = []
            kv_end_pairs = []
            for key in exon_dict_list.keys():
                kv_start_pairs.append((key[0], key))
                kv_end_pairs.append((key[1], key))
            tree_start = AVLTree(kv_start_pairs)
            tree_end = AVLTree(kv_end_pairs)
            for read in read_list:
                try:
                    item_start = tree_start.floor_item(read)
                    item_end = tree_end.ceiling_item(read)
                    if item_start[1][0] <= read <= item_start[1][1]:
                        exon_dict[chrom][item_start[1]] += 1
                        total_hits += 1
                    # Check the end item only if the exons from start_tree and end_tree are different
                    if item_start[1] != item_end[1]:
                        if item_end[1][0] <= read <= item_end[1][1]:
                            exon_dict[chrom][item_start[1]] += 1
                            total_hits += 1
                except KeyError:
                    pass

            # read_list = sorted(read_dict[chrom], reverse=False)
            # exon_list = sorted(exon_dict[chrom].keys(), key=lambda x: x[0])
            #
            # Read first and exon next
            # exon_index = 0
            # for read in read_list:
            #     for i in range(exon_index, len(exon_list)):
            #         if exon_list[i][0] <= read <= exon_list[i][1]:
            #             exon_dict[chrom][exon_list[i]] += 1
            #             total_hits += 1
            #         elif read > exon_list[i][1]:
            #             exon_index = i
            sys.stdout.write('>>> Finished chromosome %s%s for file ( %s )\n' % (chrom[:20],
                                                                               '' if len(chrom) <= 20 else '...',
                                                                               filename))
            sys.stdout.flush()
            time.sleep(1)
    sys.stdout.write('>>> Creating files and cleaning up... ( %s )\n' % filename)
    sys.stdout.flush()
    write_all_to_file(directory, exon_dict, total_reads, total_hits, filename, summary_folder, chromosomes_folder)
    # Time elapsed
    temp = time.time() - start_time
    hours = temp // 3600
    temp = temp - 3600 * hours
    minutes = temp // 60
    seconds = temp - 60 * minutes
    sys.stdout.write('>>> Finished in %d hr, %d min, %d sec for file ( %s )\n' % (hours, minutes, seconds, filename))
    sys.stdout.flush()

def gene_count(directory, summary_folder, chromosomes_folder, input_folder, chromosomes_list, sam_file_list):
    num_cores = Parallel.cpu_count()
    print ">>> Using %d Processor Cores" % (num_cores - 1)
    Parallel.Parallel(n_jobs=num_cores-1)(Parallel.delayed(lets_count)(directory, summary_folder, chromosomes_folder,
                                                                       input_folder, chromosomes_list, f) for f in
                                                                      sam_file_list)


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
    processed_file_list = fileio.get_file_list(main_directory, summary_folder, ".csv")
    for processed_file in processed_file_list:
        for sam_file in sam_file_list:
            if processed_file.replace("_summary.csv", "") == sam_file[:-4]:
                sam_file_list.remove(sam_file)
                break
    # Gets list of chromosomes from Y2Hreadme.txt file
    chromosomes_list = fileio.get_chromosomes_list(main_directory, chromosomes_list_name, printio)
    if len(sam_file_list) > 0:
        gene_count(main_directory, summary_folder, chromosomes_folder, input_folder, chromosomes_list, sam_file_list)
