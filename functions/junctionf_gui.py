import os
import sys
import struct
import cPickle
import subprocess
from sys import platform as _platform
from collections import Counter

import libraries.joblib.parallel as Parallel
import functions.process as process
import functions.structures as sts

class junctionf():
    def __init__(self, f, p):
        self.fileio = f
        self.printio = p
        self.process = process.process()
        self.blast_pipe = None
        self._spin = None

    def sigterm_handler(self, _signo, _stack_frame):
        self.blast_pipe.terminate()
        self._spin.stop()
        if self.blast_pipe < 0:
            print ">>> Terminated Process (%d). Now Exiting Gracefully!" % self.blast_pipe
            sys.stdout.flush()
        else:
            print ">>> All Process Terminated. Exiting Gracefully!"
            sys.stdout.flush()
        sys.exit()

    def _getjunction(self, begin):
        var = ''
        infile = open(os.path.join(os.curdir, "Y2Hreadme.txt"), 'r')
        for line in infile:
            if begin in line:
                var = (next(infile))
        infile.close()
        return var

    def _get_unprocessed_files(self, list, suffix1, processed_list, suffix2):
        for processed_file in processed_list:
            for f in list:
                if f.replace(suffix1, "") == processed_file.replace(suffix2, ""):
                    list.remove(f)
                    break
        return list

    def junction_search(self, directory, junction_folder, input_data_folder, blast_results_folder,
                        blast_results_query, junctions_array, exclusion_sequence):
        # junction_sequence = self._getjunction(">junctionseq")
        exclusion_sequence.upper()
        jseqs = self._make_search_junctions(junctions_array)
        print ">>> The primary, secondary, and tertiary sequences searched are:"
        sys.stdout.flush()
        unmapped_sam_files = self.fileio.get_sam_filelist(directory, input_data_folder)
        processed_file_list = self.fileio.get_file_list(directory, blast_results_query, ".bqa")
        unmapped_sam_files = self._get_unprocessed_files(unmapped_sam_files, ".sam", processed_file_list, ".bqa")

        print '>>> Starting junction search.'
        sys.stdout.flush()

        for f in unmapped_sam_files:
            open(filename)
            filename = os.path.join(directory, input_data_folder, f)
            input_filehandle = open(filename)
            input_file_size = os.path.getsize(filename)
            output_filehandle = open(os.path.join(directory, junction_folder, f.replace(".sam", '.junctions.txt')), 'w')
            # self._search_for_HA(input_file, junct1, junct2, junct3, exclusion_sequence, output_file, f, input_file_size)
            # self._search_junctions(input_file, junction_sequence, output_file)
            self._search_for_junctions(input_filehandle, jseqs, exclusion_sequence, output_filehandle, f, input_file_size)
            output_filehandle.close()
            input_filehandle.close()
        self._multi_convert(directory, junction_folder, blast_results_folder, blast_results_query)

    def _multi_convert(self, directory, infolder, outfolder, blast_results_query):
        file_list = self.fileio.get_file_list(directory, infolder, ".txt")
        processed_file_list = self.fileio.get_file_list(directory, blast_results_query, ".bqa")
        file_list = self._get_unprocessed_files(file_list, ".junctions.txt", processed_file_list, ".bqa")
        print ' '
        for f in file_list:
            self.fileio.make_FASTA(os.path.join(directory, infolder, f),
                                   os.path.join(directory, outfolder, f[:-4] + ".fa"))

    def blast_search(self, directory, db_name, blast_results_folder, blast_results_query):
        platform_specific_path = 'osx'
        suffix = ''
        if _platform == "linux" or _platform == "linux2":
            platform_specific_path = 'linux'
        elif _platform == "darwin":
            platform_specific_path = 'osx'
        elif _platform.startswith('win'):
            platform_specific_path = 'windows'
            suffix = '.exe'
        bit_size = 'x' + str(struct.calcsize("P") * 8)
        blast_path = os.path.join(os.curdir, 'ncbi_blast', 'bin', platform_specific_path, bit_size)
        # self.fileio.check_path(os.curdir, blast_path, 'Cannot find relevant Blast programs in Resources folder')
        blast_db = os.path.join(os.curdir, 'ncbi_blast', 'db')
        # database_list = self.fileio.get_file_list(blast_db, ".fa")
        # selection = select.Selection_Dialog()
        # selection.windowTitle('Blast Database Selection')
        # selection.populate_list(database_list)
        # selection.exec_()
        # selection.activateWindow()
        # db_selection = selection.selection
        db_path = os.path.join(blast_db, db_name)
        print ">>> Selected Blast DB: %s" % db_name
        sys.stdout.flush()
        file_list = self.fileio.get_file_list(directory, blast_results_folder, ".fa")
        processed_file_list = self.fileio.get_file_list(directory, blast_results_query, ".bqa")
        file_list = self._get_unprocessed_files(file_list, ".junctions.txt", processed_file_list, ".bqa")
        for file_name in file_list:
            output_file = os.path.join(directory, blast_results_folder, file_name.replace(".junctions.fa", '.blast.txt'))
            blast_command_list = [os.path.join(blast_path, 'blastn' + suffix),
                                  '-query', os.path.join(directory, 'blast_results', file_name), '-db', db_path,
                                  '-task',  'blastn', '-dust', 'no', '-num_threads', str(Parallel.cpu_count()),
                                  '-outfmt', '7', '-out', output_file, '-evalue', '0.2', '-max_target_seqs', '10']
            # blast_command = " ".join(blast_command_list)
            print ">>> Running BLAST search for file: " + file_name
            sys.stdout.flush()
            # os.system(blast_command)
            self.blast_pipe = subprocess.Popen(blast_command_list, shell=False)
            self.blast_pipe.wait()

    def generate_tabulated_blast_results(self, directory, blast_results_folder, blast_results_query_folder, gene_list_file):
        blast_list = self.fileio.get_file_list(directory, blast_results_folder, ".txt")
        processed_file_list = self.fileio.get_file_list(directory, blast_results_query_folder, ".bqa")
        blast_list = self._get_unprocessed_files(blast_list, ".blast.txt",  processed_file_list, ".bqa")

        for blasttxt in blast_list:
            print ">>> Parsing BLAST results file %s ..." % blasttxt
            blast_dict, accession_dict, gene_dict = self._blast_parser(directory, blast_results_folder,
                                                                       blasttxt, gene_list_file)
            # for key in blast_dict.keys():
            #     if key not in ['total', 'pos_que']:
            #         stats = {'in_orf'  : 0, 'in_frame': 0, 'downstream': 0,
            #                  'upstream': 0, 'not_in_frame': 0,
            #                  'intron'  : 0, 'backwards': 0, 'frame_orf': 0, 'total': 0
            #                  }
            #         for nm in blast_dict[key].keys():
            #             blast_dict[key][nm] = list(set(blast_dict[key][nm]))
            #             for j in blast_dict[key][nm]:
            #                 j.ppm = blast_dict['pos_que'][j.pos_que] * 1000000 / blast_dict['total']
            #                 stats[j.frame] += 1
            #                 stats[j.orf] += 1
            #                 if j.frame_orf:
            #                     stats["frame_orf"] += 1
            #                 stats['total'] += 1
            #         blast_dict[key]['stats'] = stats

            blast_dict.pop('pos_que')
            blast_query_p = open(os.path.join(directory, blast_results_query_folder,
                                              blasttxt.replace(".blast.txt", ".bqp")), "wb")
            lists_p = open(os.path.join(directory, blast_results_query_folder,
                                              blasttxt.replace(".blast.txt", ".bqa")), "wb")
            cPickle.dump(blast_dict, blast_query_p)
            cPickle.dump([accession_dict, gene_dict], lists_p)
            blast_query_p.close()
            lists_p.close()
        self.fileio.remove_file(directory, blast_results_folder,
                                self.fileio.get_file_list(directory, blast_results_folder, ".fa"))

    def _junctions_in_read(self, read, jseqs):
        match_index = -1
        junction_index = -1
        for i, j in enumerate(jseqs):
            if j in read:
                match_index = read.index(j)
                junction_index = i
        return (junction_index, match_index)

    def _search_for_junctions(self, input_filehandle, jseqs, exclusion_sequence, output_filehandle, f, input_file_size):
        hits_count = 0
        def check_matching_criteria(l, indexes, jseqs, read):
            value = 0
            if indexes[0] != -1:
                junction = jseqs[indexes[0]]
                downstream_rf = read[len(junction) + indexes[1] + (indexes[0] % 3) * 4:]
                if len(downstream_rf) > 25:
                    if exclusion_sequence not in downstream_rf or exclusion_sequence == '':
                        value = 1
                        protein_sequence = self.process.translate_orf(downstream_rf)
                        output_filehandle.write(" ".join(l[:5]) + " " + l[9] + " " + downstream_rf
                                                + " " + protein_sequence + "\n")
            return value

        reads_count = 0
        for line in input_filehandle:
            line_split = line.strip().split()
            if line_split[0][0] != "@" and line_split[2] == "*":
                reads_count += 1
                if reads_count % 5000 == 0:
                    sys.stdout.write('\rRead %.3f%% of file...' % (input_filehandle.tell() * 100.0 / input_file_size))
                    sys.stdout.flush()
                sequence_read = line_split[9]
                rev_sequence_read = self.process.reverse_complement(sequence_read)
                fwd_indexes = self._junctions_in_read(sequence_read, jseqs)
                hit = check_matching_criteria(line_split, fwd_indexes, jseqs, sequence_read)
                if hit == 0:
                    rev_indexes = self._junctions_in_read(rev_sequence_read, jseqs)
                    hit = check_matching_criteria(line_split, rev_indexes, jseqs, rev_sequence_read)
                hits_count += hit

    def _make_search_junctions(self, junctions_array):
        jseqs = []
        for junc in junctions_array:
            jseqs.append(junc[35:50])
            jseqs.append(junc[31:46])
            jseqs.append(junc[27:42])
        return jseqs

    def _get_accession_number_list(self, gene_list_file):
        fh = open(os.path.join('lists', gene_list_file), 'r')
        gene_list = {}
        for line in fh.readlines():
            split = line.split()
            gene_list[split[0]] = {'gene_name' : split[1],
                                   'orf_start' : int(split[6]) + 1,
                                   'orf_stop'  : int(split[7]),
                                   'mRNA'      : split[9],
                                   'intron'    : split[8],
                                   'chromosome': split[2]
                                   }
        return gene_list

    def _blast_parser(self, directory, infolder, fileName, gene_list_file):
        blast_results_handle = open(os.path.join(directory, infolder, fileName), 'r')
        gene_list = self._get_accession_number_list(gene_list_file)
        blast_results_count = 0
        print_counter = 0
        previous_bitscore = 0
        results_dictionary = {}
        accession_dict = {}
        gene_dict = {}
        collect_results = 'n'
        pos_que = []
        for line in blast_results_handle.readlines():
            line.strip()
            split = line.split()
            if "BLASTN" in line:
                blast_results_count += 1
                print_counter += 1
                previous_bitscore = 0
                if print_counter == 90000: #this if loop is purely for output purposes
                    sys.stdout.write('.')
                    print_counter = 0
            elif "hits" in line and int(split[1]) < 100:  # limits number of blast hits for single read to less than 100
                collect_results = 'y'
            elif split[0] != '#' and collect_results == 'y' and float(split[2]) > 98 and \
                            float(split[11]) > 50.0 and float(split[11]) > previous_bitscore:
                previous_bitscore = float(split[11]) * 0.98
                nm_number = split[1]
                gene_name = gene_list[nm_number]['gene_name']
                accession_dict[nm_number] = gene_list[nm_number]['gene_name']
                if gene_name not in gene_dict.keys():
                    gene_dict[gene_name] = [nm_number]
                else:
                    gene_dict[gene_name].append(nm_number)

                pq = nm_number + "-" + split[8] + "-" + split[6]
                j = sts.jcnt()
                j.position = int(split[8])
                j.query_start = int(split[6])
                j.pos_que = pq
                pos_que.append(pq)
                fudge_factor = j.query_start - 1
                frame = j.position - gene_list[nm_number]['orf_start'] - fudge_factor
                if frame % 3 == 0 or frame == 0:
                    j.frame = "in_frame"
                else:
                    j.frame = "not_in_frame"

                if gene_list[nm_number]['intron'] == "INTRON":
                    j.frame = "intron"

                if int(split[9]) - j.position < 0:
                    j.frame = "backwards"

                if j.position < gene_list[nm_number]['orf_start']:
                    j.orf = "upstream"
                elif j.position > gene_list[nm_number]['orf_stop']:
                    j.orf = "downstream"
                else:
                    j.orf = "in_orf"

                if j.frame == 'in_frame' and j.orf == 'in_orf':
                        j.frame_orf = True

                if gene_name not in results_dictionary.keys():
                    results_dictionary[gene_name] = {}
                    results_dictionary[gene_name][nm_number] = [j]
                else:
                    if nm_number not in results_dictionary[gene_name].keys():
                        results_dictionary[gene_name][nm_number] = [j]
                    else:
                        results_dictionary[gene_name][nm_number].append(j)
            else:
                collect_results = 'n'
        results_dictionary['total'] = blast_results_count
        results_dictionary['pos_que'] = Counter(pos_que)
        blast_results_handle.close()
        return results_dictionary, accession_dict, gene_dict

    # def _search_junctions(self, infile, junction_sequence, outfile):
    #     def longest_common_substring(s1, s2):
    #         m = [[0] * (1 + len(s2)) for i in xrange(1 + len(s1))]
    #         longest, x_longest = 0, 0
    #         for x in xrange(1, 1 + len(s1)):
    #             for y in xrange(1, 1 + len(s2)):
    #                 if s1[x - 1] == s2[y - 1]:
    #                     m[x][y] = m[x - 1][y - 1] + 1
    #                     if m[x][y] > longest:
    #                         longest = m[x][y]
    #                         x_longest = x
    #                 else:
    #                     m[x][y] = 0
    #         return s1[x_longest - longest: x_longest]
    #     reads = 0
    #     iterations = 0
    #     reverse_junction_sequence = self.process.reverse_complement(junction_sequence)
    #     for line in infile.readlines():
    #         split = line.split()
    #         if split[0][0] != '@' and split[2] == '*':
    #             read = split[9]
    #             reads += 1
    #             iterations += 1
    #             if iterations == 5000:
    #                 iterations = 0
    #                 sys.stdout.write('.', )
    #                 sys.stdout.flush()
    #             substring = longest_common_substring(junction_sequence, read)
    #             rev_substring = longest_common_substring(reverse_junction_sequence, read)
    #             jloc = junction_sequence.find(substring) + len(substring)
    #             jloc_rev = reverse_junction_sequence.find(rev_substring) + len(rev_substring)
    #             rloc = read.find(substring) + len(substring) + len(junction_sequence) - jloc
    #             rloc_rev = read.find(reverse_junction_sequence) + len(rev_substring) + \
    #                        len(reverse_junction_sequence) - jloc_rev
    #
    #             if jloc >= len(junction_sequence) - 1 and len(read) - rloc > 25 and len(substring) > 15:
    #                 outfile.write(str(split[0]) + " "
    #                               + str(split[1]) + " "
    #                               + str(split[2]) + " "
    #                               + str(split[3]) + " "
    #                               + str(split[9]) + " "
    #                               + read[rloc:] + " "
    #                               + self.process.translate_orf(read[rloc:]) + "\n")
    #                 continue
    #
    #             if jloc_rev >= len(reverse_junction_sequence) - 1 and len(read) - rloc_rev > 25 and len(rev_substring) > 15:
    #                 outfile.write(str(split[0]) + " "
    #                               + str(split[1]) + " "
    #                               + str(split[2]) + " "
    #                               + str(split[3]) + " "
    #                               + str(split[9]) + " "
    #                               + read[rloc_rev:] + " "
    #                               + self.process.translate_orf(read[rloc_rev:]) + "\n")


    # def _search_for_HA(self, infile, primaryJunct, secondaryJunct, tertiaryJunct, exclusion_sequence, OutFile, f,
    #                    input_file_size):
    #     HA = primaryJunct
    #     HArev = self.process.reverse_complement(HA)
    #     HA2 = secondaryJunct
    #     HA2rev = self.process.reverse_complement(HA2)
    #     HA3 = tertiaryJunct
    #     HA3rev = self.process.reverse_complement(HA2)
    #     Hits2 = 0
    #     Hits = 0
    #     reads = 0
    #     iterations = 0
    #     toggle = 0
    #     self.printio.print_progress(f, 0, 0, 0, 1)
    #     for line in infile:
    #         line.strip()
    #         splitLine = line.split()
    #         if splitLine[0][0] != '@' and splitLine[2] == '*':
    #             reads += 1
    #             iterations += 1
    #             if iterations == 5000:
    #                 iterations = 0
    #                 sys.stdout.write('\rRead %.3f%% of file...' % (infile.tell() * 100.0 / input_file_size))
    #                 sys.stdout.flush()
    #
    #             if HA in splitLine[9] or HArev in splitLine[9] or HA2 in splitLine[9] or \
    #                             HA2rev in splitLine[9] or HA3 in splitLine[9] or HA3rev in splitLine[9]:
    #                 Hits += 1
    #                 if HA in splitLine[9]:
    #                     HAindex = splitLine[9].index(HA)
    #                     DSRF = splitLine[9][(HAindex + len(HA)):]
    #                     if len(DSRF) > 25:
    #                         if exclusion_sequence not in DSRF or exclusion_sequence == '':
    #                             Protein = self.process.translate_orf(DSRF)
    #                             Hits2 += 1
    #                             toggle = 1
    #                 elif HArev in splitLine[9]:
    #                     HARevCom = self.process.reverse_complement(splitLine[9])
    #                     HAindex = HARevCom.index(HA)
    #                     DSRF = HARevCom[(HAindex + len(HA)):]
    #                     if len(DSRF) > 25:
    #                         if exclusion_sequence not in DSRF or exclusion_sequence == '':
    #                             Protein = self.process.translate_orf(DSRF)
    #                             Hits2 += 1
    #                             toggle = 1
    #                 elif HA2 in splitLine[9]:
    #                     HA2index = splitLine[9].index(HA2)
    #                     DSRF = splitLine[9][(HA2index + len(HA2) + 4):]
    #                     if len(DSRF) > 25:
    #                         if exclusion_sequence not in DSRF or exclusion_sequence == '':
    #                             Protein = self.process.translate_orf(DSRF)
    #                             Hits2 += 1
    #                             toggle = 1
    #                 elif HA2rev in splitLine[9]:
    #                     HARevCom = self.process.reverse_complement(splitLine[9])
    #                     HA2index = HARevCom.index(HA2)
    #                     DSRF = HARevCom[(HA2index + len(HA2) + 4):]
    #                     if len(DSRF) > 25:
    #                         if exclusion_sequence not in DSRF or exclusion_sequence == '':
    #                             Protein = self.process.translate_orf(DSRF)
    #                             Hits2 += 1
    #                             toggle = 1
    #                 elif HA3 in splitLine[9]:
    #                     HA3index = splitLine[9].index(HA3)
    #                     DSRF = splitLine[9][(HA3index + len(HA3) + 8):]
    #                     if len(DSRF) > 25:
    #                         if exclusion_sequence not in DSRF or exclusion_sequence == '':
    #                             Protein = self.process.translate_orf(DSRF)
    #                             Hits2 += 1
    #                             toggle = 1
    #                 elif HA3rev in splitLine[9]:
    #                     HARevCom = self.process.reverse_complement(splitLine[9])
    #                     HA3index = HARevCom.index(HA3)
    #                     DSRF = splitLine[9][(HA3index + len(HA3) + 8):]
    #                     if len(DSRF) > 25:
    #                         if exclusion_sequence not in DSRF or exclusion_sequence == '':
    #                             Protein = self.process.translate_orf(DSRF)
    #                             Hits2 += 1
    #                             toggle = 1
    #                 if toggle == 1:
    #                     if exclusion_sequence not in DSRF or exclusion_sequence == '':
    #                         OutFile.write(str(splitLine[0]) + " " + str(splitLine[1]) + " " + str(splitLine[2]) + " " + str(
    #                                 splitLine[3]) + " " + str(splitLine[9]) + " " + DSRF + " " + Protein + "\n")
    #                         toggle = 0
