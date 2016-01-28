import re
import os
import sys
import glob
from libraries.termcolor import cprint
import functions.printio as p

class fileio():
    """Functions to process files and directories"""

    def __init__(self):
        self.print_grey_on_cyan = lambda x: cprint(x, 'grey', 'on_cyan')
        self.print_grey_on_red = lambda x: cprint(x, 'grey', 'on_red')
        self.print_grey_on_yellow = lambda x: cprint(x, 'grey', 'on_yellow')
        self.printio = p.printio()
    
    def create_new_folder(self, folder):

        folder_path = os.path.join(os.curdir, folder)
        if not os.path.exists(os.path.join(os.curdir, folder)):
            os.mkdir(folder_path)
        else:
            self.print_grey_on_yellow("\n>>> WARNING:  Path " + folder + " already exists!")
            if os.path.exists(folder_path): 
                print 'Previous data output folders exist'
                print 'If there are files in ' + folder + ', '
                print 'running this program will add to them or write over them.'
                print 'It is recommended that the folders be moved or the files in them be moved.'

    def change_file_name(self, folder, oldsuffix, newsuffix):
        var = len(oldsuffix)
        for filename in glob.iglob(os.path.join(folder, '*' + oldsuffix)):
            os.rename(filename, filename[:-var] + newsuffix)

    def get_file_list(self, folder, suffix):
        fileList = [x for x in os.listdir(os.path.join(os.curdir, folder)) if os.path.splitext(x)[1] in (suffix)]
        for file in fileList:
            if re.match('\.DS_Store', file):
                fileList.remove(file)
        return(fileList)

    def check_path(self, folder, comment):
        if not os.path.exists(os.path.join(os.curdir, folder)):
            self.print_grey_on_red('\n>>> ERROR: %s' % comment)
            sys.exit()


    def get_sam_filelist(self, infolder):
        
        file_list = []
        
        self.check_path(infolder, "Cannot find %s folder" % infolder)
        self.check_path(os.path.join(os.curdir, "Resources", "mm10GeneDict.p"), "Cannot find mm10GeneDict.p file in Resources folder")
        
        if os.path.exists(os.path.join(os.curdir, infolder)):
            file_list = self.get_file_list(infolder, '.sam')
            if len(file_list) == 0:
                self.print_grey_on_red('\n>>> ABORTED: There appear to be no .sam files in the folder %s to process\n' % infolder)
                exit()

        a = self.printio.get_raw_input()
        if a == 'N' or a == 'n':
            self.print_grey_on_red('>>> ABORTED!')
            quit()
        
        print '\n....\n'

        return file_list

    def get_chromosomes_list(self, tag, printio_handle):
        chromList = []
        try:
            comment_filehandle = open(os.path.join(os.curdir, "Resources", "Y2Hreadme.txt"), 'r')
        except:
            print 'Cannot find the Y2Hreadme file in Resources folder to get chromosome list'
            self.print_grey_on_red('>>> ABORTED!')
            exit()

        for chr_name in printio_handle.get_text_block(comment_filehandle, tag):
            chromList.append(chr_name.rstrip())
        comment_filehandle.close()
        return chromList

    def remove_file(self, folder, file_list):
        for fi in file_list:
            os.remove(os.path.join(os.curdir, folder, fi))
            self.print_grey_on_red("\nCleaned up file %s in folder %s" % (fi, folder))

    def input_data_check(self, input_data_folder, file_extenstion, folders=[]):
        self.check_path(input_data_folder, 'Cannot find %s folder' % input_data_folder)
        if os.path.exists(os.path.join(os.curdir, input_data_folder)):
            filecheck = self.get_file_list(input_data_folder, file_extenstion)
            if len(filecheck) == 0:
                self.print_grey_on_red('\n>>> ERROR: There appear to be no %s files in the folder %s to '
                                       'process' % (input_data_folder, file_extenstion))
        if len(folders) > 0:
            if True in map(lambda x: os.path.exists(os.path.join(os.curdir, x)), folders):
                print "\n"
                self.print_grey_on_yellow('>>> WARNING: Previous data output folders exist')
                print 'If there are files in these folders, running this program will reprocess them.'
                print 'It is recommended that the folders be moved or the files in them be moved.'

        a = self.printio.get_raw_input()
        if a == 'N' or a == 'n':
            print '...aborted'
            quit()

    def make_FASTA(self, junctionFile, outputFile):
        counter = 0
        inFile = open(junctionFile, 'r')
        outFile = open(outputFile, 'w')
        for line in inFile:
            line.strip()
            split = line.split()
            try:
                outFile.write(">%s\n%s\n" % (str(split[0]), str(split[5])))
                counter += 1
            except:
                continue       
        inFile.close()
        outFile.close()
        print 'Converted ', counter, 'junctions in ', junctionFile, ' to a FASTA file'