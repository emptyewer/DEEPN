import os
import re
import sys
import time
import struct
import cPickle
import subprocess
from sys import platform as _platform

import libraries.joblib.parallel as Parallel
import functions.process as process
import functions.spinbar as spinbar

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print '>>> Function %r finished %2.2f sec' % (method.__name__, te-ts)
        sys.stdout.flush()
        return result
    return timed

class junctionf():
    """

    """

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

    @timeit
    def junction_search(self, directory, junction_folder, input_data_folder,
                        blast_results_folder, junction_sequence, exclusion_sequence):
        # junction_sequence = self._getjunction(">junctionseq")
        junction_sequence.upper()
        exclusion_sequence.upper()
        junct1, junct2, junct3 = self._make_search_junctions(junction_sequence)
        print ">>> The primary, secondary, and tertiary sequences searched are:"
        sys.stdout.flush()
        self.printio.print_progress(0, junct1, junct2, junct3, 4)
        unmapped_sam_files = self.fileio.get_sam_filelist(directory, input_data_folder)
        
        print '>>> Starting junction search.'
        sys.stdout.flush()

        for f in unmapped_sam_files:
            input_file = open(os.path.join(directory, input_data_folder, f), 'r')
            output_file = open(os.path.join(directory, junction_folder, f + '_jTEMP'), 'w')
            self._search_for_HA(input_file, junct1, junct2, junct3, exclusion_sequence, output_file, f)
            output_file.close()
        
        self.fileio.change_file_name(directory, junction_folder, ".sam_jTEMP", ".Junctions.txt")
        self._multi_convert(directory, junction_folder, blast_results_folder)

    @timeit
    def blast_search(self, directory, db_name, blast_results_folder):
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
        for file_name in self.fileio.get_file_list(directory, blast_results_folder, ".fa"):
            output_file = os.path.join(directory, blast_results_folder, file_name + '.blast.txt')
            blast_command_list = [os.path.join(blast_path, 'blastn' + suffix),
                                  '-query', os.path.join(directory, 'blast_results', file_name), '-db', db_path,
                                  '-task',  'blastn', '-dust', 'no', '-num_threads', str(Parallel.cpu_count()),
                                  '-outfmt', '7', '-out', output_file, '-evalue', '0.2', '-max_target_seqs', '10']
            # blast_command = " ".join(blast_command_list)
            print ">>> Running BLAST search for file: " + file_name
            sys.stdout.flush()
            self._spin = spinbar.SpinCursor(msg="Please wait for BLAST to finish...", speed=2)
            self._spin.start()
            # os.system(blast_command)
            self.blast_pipe = subprocess.Popen(blast_command_list, shell=False)
            self.blast_pipe.wait()
            self._spin.stop()

    @timeit
    def generate_tabulated_blast_results(self, directory, blast_results_folder, blast_results_query_folder):
        blasttxtList = self.fileio.get_file_list(directory, blast_results_folder, ".txt")
        for blasttxt in blasttxtList:
            self._spin = spinbar.SpinCursor(msg="Parsing BLAST results file %s ..." % blasttxt)
            self._spin.start()
            blast_dict = self._blast_parser(directory, blast_results_folder, blasttxt)
            dotPfile = open(os.path.join(directory, blast_results_query_folder, blasttxt + ".p"), "wb")
            cPickle.dump(blast_dict, dotPfile)
            self._spin.stop()
        self.fileio.change_file_name(directory, blast_results_query_folder, ".Junctions.txtTEMP.fa.blast.txt.p",
                                     ".blast.txt.p")
        self.fileio.change_file_name(directory, blast_results_folder, ".Junctions.txtTEMP.fa.blast.txt", ".blast.txt")
        self.fileio.remove_file(directory, blast_results_folder,
                                self.fileio.get_file_list(directory, blast_results_folder, ".fa"))

    def _multi_convert(self, directory, infolder, outfolder):
        fileList = self.fileio.get_file_list(directory, infolder, ".txt")
        print ' '
        for f in fileList:
            self.fileio.make_FASTA(os.path.join(directory, infolder, f), os.path.join(directory, outfolder, f + "TEMP.fa"))
        return
    
    def _search_for_HA(self, infile, primaryJunct, secondaryJunct, tertiaryJunct, exclusion_sequence, OutFile, f):
        HA = primaryJunct
        HArev = self.process.reverse_complement(HA)
        HA2 = secondaryJunct 
        HA2rev = self.process.reverse_complement(HA2)
        HA3 = tertiaryJunct 
        HA3rev = self.process.reverse_complement(HA2)
        Hits2 = 0
        Hits = 0
        reads = 0
        iterations = 0
        toggle = 0

        self.printio.print_progress(f, 0, 0, 0, 1)
        for line in infile:
            line.strip()
            splitLine = line.split()
            if splitLine[0][0] != '@':
                reads += 1
                iterations += 1
                if iterations == 25000:
                    iterations = 0
                    sys.stdout.write('\b.',)
                    sys.stdout.flush()
                          
                if HA in splitLine[9] or HArev in splitLine[9] or HA2 in splitLine[9] or HA2rev in splitLine[9] or HA3 in splitLine[9] or HA3rev in splitLine[9]:
                    Hits += 1
                    if HA in splitLine[9]:
                        HAindex = splitLine[9].index(HA)
                        DSRF = splitLine[9][(HAindex + len(HA)):]
                        if len(DSRF) > 25:
                            if exclusion_sequence != DSRF:
                                Protein = self.process.translate_orf(DSRF)
                                Hits2 += 1
                                toggle = 1
                    elif HArev in splitLine[9]:
                        HARevCom = self.process.reverse_complement(splitLine[9])
                        HAindex = HARevCom.index(HA)
                        DSRF = HARevCom[(HAindex + len(HA)):]
                        if len(DSRF) > 25:
                            if exclusion_sequence != DSRF:
                                Protein = self.process.translate_orf(DSRF)
                                Hits2 += 1
                                toggle = 1
                    elif HA2 in splitLine[9]:
                        HA2index = splitLine[9].index(HA2)
                        DSRF = splitLine[9][(HA2index+len(HA2)+4):]
                        if len(DSRF) > 25:
                            if exclusion_sequence != DSRF:
                                Protein = self.process.translate_orf(DSRF)
                                Hits2 += 1
                                toggle = 1
                    elif HA2rev in splitLine[9]:
                        HARevCom = self.process.reverse_complement(splitLine[9])
                        HA2index = HARevCom.index(HA2)
                        DSRF = HARevCom[(HA2index + len(HA2)+4):]
                        if len(DSRF) > 25:
                            if exclusion_sequence != DSRF:
                                Protein = self.process.translate_orf(DSRF)
                                Hits2 += 1
                                toggle = 1
                    elif HA3 in splitLine[9]:
                        HA3index = splitLine[9].index(HA3)
                        DSRF = splitLine[9][(HA3index+len(HA3)+8):]
                        if len(DSRF) > 25:
                            if exclusion_sequence != DSRF:
                                Protein = self.process.translate_orf(DSRF)
                                Hits2 += 1
                                toggle = 1
                    elif HA3rev in splitLine[9]:
                        HARevCom = self.process.reverse_complement(splitLine[9])
                        HA3index = HARevCom.index(HA3)
                        DSRF = splitLine[9][(HA3index+len(HA3)+8):]
                        if len(DSRF) > 25:
                            if exclusion_sequence != DSRF:
                                Protein = self.process.translate_orf(DSRF)
                                Hits2 += 1
                                toggle = 1
                    if toggle == 1:
                        if exclusion_sequence != DSRF:
                            OutFile.write(str(splitLine[0]) + " " + str(splitLine[1]) + " " + str(splitLine[2]) + " " + str(splitLine[3]) + " " + str(splitLine[9]) + " " + DSRF + " " + Protein + "\n")
                            toggle = 0

    def _make_search_junctions(self, HAseq):
        x = HAseq[35:50]
        y = HAseq[31:46]
        z = HAseq[27:42] 
        return[x, y, z]

    def _blast_parser(self, directory, infolder, fileName):
        I = open(os.path.join(directory, infolder, fileName), 'r')
        counter = 0
        total = 0
        total2 = 0
        variable = 0
        Dict = {}
        toggle = 'n'
        for line in I:
            line.strip()
            split = line.split()
            if "BLASTN" in line:
                total += 1
                total2 += 1
                variable = 0
                if total2 == 90000:
                        sys.stdout.write('.')
                        total2 = 0
            elif "hits" in line and int(split[1]) < 100:  # limits number of blast returns for single read
                    toggle = 'y'

            elif line[0] != '#' and toggle == 'y' and float(split[2]) > 98 and float(split[11]) > 50.0 and float(split[11]) > variable:
                variable = float(split[11])*0.98
                counter += 1

                split = line.split()
                junctIndex = split[8]+'-'+split[6]
                if split[1] not in Dict.keys():
                    Dict[split[1]] = [junctIndex]
                else:
                    Dict[split[1]].append(junctIndex)
            else:
                toggle = 'n'
        Dict['total'] = total 
        I.close()
        return Dict
