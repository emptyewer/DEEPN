
import os
import sys
import time
import cPickle
from sys import platform as _platform

from libraries.termcolor import cprint
import libraries.joblib.parallel as Parallel
import functions.fileio as f
import functions.printio as p
import functions.process as process
import functions.spinbar as spinbar

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        cprint('\n>>> Function %r finished %2.2f sec\n' % (method.__name__, te-ts), 'green')
        return result
    return timed


class junctionf():
    """

    """
    def __init__(self):
        self.fileio = f.fileio()
        self.printio = p.printio()
        self.process = process.process()
        self.print_grey_on_cyan = lambda x: cprint(x, 'grey', 'on_cyan')
        self.print_grey_on_red = lambda x: cprint(x, 'grey', 'on_red')
        self.print_grey_on_yellow = lambda x: cprint(x, 'grey', 'on_yellow')

    def _getjunction(self, begin):
        infile = open(os.path.join(os.curdir, "Resources", "Y2Hreadme.txt"), 'r')
        for line in infile:
            if begin in line:
                var = (next(infile))
        infile.close()
        return var

    @timeit
    def junction_search(self, junction_folder, input_data_folder, blast_results_folder):
        junction_sequence = self._getjunction(">junctionseq")                                     
        junct1, junct2, junct3 = self._make_search_junctions(junction_sequence)
        self.printio.print_comment("Comment2")
        self.printio.print_progress(0, junct1, junct2, junct3, 4)
        self.fileio.create_new_folder(junction_folder)
        unmapped_sam_files = self.fileio.get_sam_filelist(input_data_folder)
        
        print '\nStarting junction search.'

        for f in unmapped_sam_files:
            input_file = open(os.path.join(os.curdir, input_data_folder, f) , 'r')
            output_file = open(os.path.join(os.curdir, junction_folder, f + '_jTEMP'), 'w')
            self._search_for_HA(input_file, junct1, junct2, junct3, output_file, f)
            output_file.close()
        
        self.fileio.change_file_name(junction_folder, ".sam_jTEMP", ".Junctions.txt")
        print "\n"
        self.fileio.create_new_folder(blast_results_folder)                             
        self._multi_convert(junction_folder, blast_results_folder)

    @timeit
    def blast_search(self):
        self.printio.print_comment("Comment3")
        platform_specific_path = 'osx'
        if _platform == "linux" or _platform == "linux2":
            platform_specific_path = 'linux'
        elif _platform == "darwin":
            platform_specific_path = 'osx'
        elif _platform == "win32":
            platform_specific_path = 'win32'
        blast_path = os.path.join(os.curdir, 'Resources', 'NCBIblastprograms', 'bin', platform_specific_path)
        self.fileio.check_path(blast_path, 'Cannot find relevant Blast programs in Resources folder')
        blast_db = os.path.join(os.curdir, 'Resources', 'NCBIblastprograms', 'db')
        database_list = self.fileio.get_file_list(blast_db, ".fa")
        print "\n"
        for i, name in enumerate(database_list):
            cprint("%d. %s" % (i+1, name), 'magenta')
        db_selection = self.printio.get_raw_input('Select the appropriate database...', str(range(1, len(database_list) + 1)))
        for file_name in self.fileio.get_file_list(os.path.join(os.curdir, 'blastResults'), ".fa"):
            output_file = os.path.join(os.curdir, 'blastResults', file_name + '.blast.txt')
            blast_command_list = [os.path.join(blast_path, 'blastnY2H'), '-query', os.path.join(os.curdir, 'blastResults', file_name), '-db', os.path.join(blast_db, database_list[int(db_selection) - 1]), '-task',  'blastn', '-dust', 'no', '-num_threads', str(Parallel.cpu_count()), '-outfmt', '7', '-out', output_file, '-evalue', '0.2', '-max_target_seqs', '10']
            blast_command = " ".join(blast_command_list)
            self.print_grey_on_cyan("\n>>> Running BLAST search for file: " + file_name)
            _spin = spinbar.SpinCursor(msg="Please wait for BLAST to finish...")
            _spin.start()
            os.system(blast_command)
            _spin.stop()

    @timeit
    def generate_tabulated_blast_results(self, blast_results_folder, blast_results_query_folder):
        blasttxtList = self.fileio.get_file_list(blast_results_folder, ".txt")
        self.fileio.create_new_folder(blast_results_query_folder)
        for blasttxt in blasttxtList:
            _spin = spinbar.SpinCursor(msg="Parsing BLAST results file %s ..." % blasttxt)
            _spin.start()
            blast_dict = self._blast_parser(blast_results_folder, blasttxt)
            dotPfile = open(os.path.join(os.curdir, blast_results_query_folder, blasttxt + ".p"), "wb")
            cPickle.dump(blast_dict, dotPfile)
            _spin.stop()
        self.fileio.change_file_name(blast_results_query_folder, ".Junctions.txtTEMP.fa.blast.txt.p", ".blast.txt.p")
        self.fileio.change_file_name(blast_results_folder, ".Junctions.txtTEMP.fa.blast.txt", ".blast.txt")
        self.fileio.remove_file(blast_results_folder, self.fileio.get_file_list(blast_results_folder, ".fa"))

    def _multi_convert(self, infolder, outfolder):
        fileList = self.fileio.get_file_list(infolder, ".txt")
        print ' '
        for f in fileList:
            self.fileio.make_FASTA(os.path.join(os.curdir, infolder, f), os.path.join(os.curdir, outfolder, f + "TEMP.fa"))
        return
    
    def _search_for_HA(self, infile, primaryJunct, secondaryJunct, tertiaryJunct,OutFile,f):
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
                if iterations == 100000:
                    iterations = 0
                    print '\b.',
                    sys.stdout.flush()
                          
                if HA in splitLine[9] or HArev in splitLine[9] or HA2 in splitLine[9] or HA2rev in splitLine[9] or HA3 in splitLine[9] or HA3rev in splitLine[9]:
                    Hits += 1
                    if HA in splitLine[9]:
                        HAindex = splitLine[9].index(HA)
                        DSRF = splitLine[9][(HAindex + len(HA)):]
                        if len(DSRF) > 25:
                              Protein = self.process.translate_orf(DSRF)
                              Hits2 += 1
                              toggle = 1
                    elif HArev in splitLine[9]:
                        HARevCom = self.process.reverse_complement(splitLine[9])
                        HAindex = HARevCom.index(HA)
                        DSRF = HARevCom[(HAindex + len(HA)):]
                        if len(DSRF) > 25:
                              Protein = self.process.translate_orf(DSRF)
                              Hits2 += 1
                              toggle = 1
                    elif HA2 in splitLine[9]:
                        HA2index = splitLine[9].index(HA2)
                        DSRF = splitLine[9][(HA2index+len(HA2)+4):]
                        if len(DSRF) > 25:
                              Protein = self.process.translate_orf(DSRF)
                              Hits2 += 1
                              toggle = 1
                    elif HA2rev in splitLine[9]:
                        HARevCom = self.process.reverse_complement(splitLine[9])
                        HA2index = HARevCom.index(HA2)
                        DSRF = HARevCom[(HA2index + len(HA2)+4):]
                        if len(DSRF) > 25:
                              Protein = self.process.translate_orf(DSRF)
                              Hits2 += 1
                              toggle = 1
                    elif HA3 in splitLine[9]:
                        HA3index = splitLine[9].index(HA3)
                        DSRF = splitLine[9][(HA3index+len(HA3)+8):]
                        if len(DSRF) > 25:
                              Protein = self.process.translate_orf(DSRF)
                              Hits2 += 1
                              toggle = 1
                    elif HA3rev in splitLine[9]:
                        HARevCom = self.process.reverse_complement(splitLine[9])
                        HA3index = HARevCom.index(HA3)
                        DSRF = splitLine[9][(HA3index+len(HA3)+8):]
                        if len(DSRF) > 25:
                              Protein = self.process.translate_orf(DSRF)
                              Hits2 += 1
                              toggle = 1
                    if toggle == 1:
                        OutFile.write(str(splitLine[0]) + " " + str(splitLine[1]) + " " + str(splitLine[2]) + " " + str(splitLine[3]) + " " + str(splitLine[9]) + " " + DSRF + " " + Protein + "\n")
                        toggle = 0

    def _make_search_junctions(self, HAseq):
        x = HAseq[35:50]
        y = HAseq[31:46]
        z = HAseq[27:42] 
        return[x, y, z]

    def _blast_parser(self, infolder, fileName):
        I = open(os.path.join(os.curdir, infolder, fileName), 'r')
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
                if split[1] not in Dict.keys():
                    Dict[split[1]] = [int(split[8])]
                else:
                    Dict[split[1]].append(int(split[8]))
            else:
                toggle = 'n'
        Dict['total'] = total 
        I.close()
        return Dict
