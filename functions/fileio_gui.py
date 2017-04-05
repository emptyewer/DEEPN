import time
import os
import glob
import sys
import subprocess
from libraries.pyper import *

class fileio():
    """Functions to process files and directories"""

    def __init__(self):
        pass

    def create_new_folder(self, directory, folder):
        folder_path = os.path.join(directory, folder)
        if not os.path.exists(os.path.join(directory, folder)):
            os.mkdir(folder_path)

    def change_file_name(self, directory, folder, oldsuffix, newsuffix):
        var = len(oldsuffix)
        for filename in glob.iglob(os.path.join(directory, folder, '*' + oldsuffix)):
            os.rename(filename, filename[:-var] + newsuffix)

    def get_file_list(self, directory, folder, suffix):
        fileList = os.listdir(os.path.join(directory, folder))
        returnList = []
        for file in fileList:
            if os.path.splitext(file)[1] == suffix:
                returnList.append(file)
        return(returnList)

    def get_exec_path(self, executable):
        if os.path.exists('/usr/local/bin/' + executable):
            return True
        if os.path.exists('/usr/bin/' + executable):
            return True
        return False

    def check_deepn_installed(self, parent):
        dout = parent.r("require('deepn')")
        dout = dout.replace(' ', '')
        dout = dout.replace('\n', '')
        if re.match('.+nopackage.+', dout):
            return False
        return True

    def verify_statmaker_installations(self, parent):
        if not self.get_exec_path('jags'):
            parent.verify_installation_btn.setText("Installing JAGS...")
            subprocess.Popen('open statistics/JAGS.pkg', shell=True)
            while not self.get_exec_path('jags'):
                time.sleep(0.5)

        if os.path.exists('/usr/local/bin/jags'):
            self.jags_path = '/usr/local/bin/jags'
        if os.path.exists('/usr/bin/jags'):
            self.jags_path = '/usr/bin/jags'

        if not self.get_exec_path('R'):
            parent.verify_installation_btn.setText("Installing R...")
            subprocess.Popen('open statistics/R.pkg', shell=True)
            while not self.get_exec_path('R'):
                time.sleep(0.5)

        if os.path.exists('/usr/local/bin/R'):
            parent.r_path = '/usr/local/bin/R'
        if os.path.exists('/usr/bin/R'):
            parent.r_path = '/usr/bin/R'

        if os.path.exists(parent.r_path):
            parent.r = R(RCMD=parent.r_path)
            if not self.check_deepn_installed(parent):
                parent.verify_installation_btn.setText("Finishing Installation...")
                subprocess.Popen(['bash install_deepn.sh ' + parent.r_path], shell=True)
                while not self.check_deepn_installed(parent):
                    time.sleep(0.5)
            else:
                parent.statusbar.showMessage("Updating DEEPN...")
                subprocess.Popen(['bash update_deepn.sh ' + parent.r_path], shell=True)

    # def check_path(self, directory, folder, comment):
    #     if not os.path.exists(os.path.join(directory, folder)):
    #         self.message.windowTitle('Aborted!')
    #         self.message.showMessage('>>> ABORTED <<<\n\n%s\n' % comment)
    #         self.message.continue_btn.setEnabled(False)
    #         self.message.exec_()
    #         self.message.activateWindow()
    #         sys.exit()


    def get_sam_filelist(self, directory, infolder):
        file_list = []
        # self.check_path(directory, infolder, "Cannot find %s folder" % infolder)
        ### $$$$$$$$$ ###
        # self.check_path(os.curdir, os.path.join("dictionaries", "mm10GeneDict.p"), "Cannot find mm10GeneDict.p file in "
        #                                                                         "dictionaries folder")
        if os.path.exists(os.path.join(directory, infolder)):
            file_list = self.get_file_list(directory, infolder, '.sam')
            # if len(file_list) == 0:
            #     self.message.windowTitle('Aborted!')
            #     self.message.showMessage('>>> ABORTED <<<\n\nThere appear to be no .sam files in the folder %s to '
            #                              'process\n' % infolder)
            #     self.message.continue_btn.setEnabled(False)
            #     self.message.exec_()
            #     self.message.activateWindow()
            #     sys.exit()
        # if self.prompt == 2:
        #     self.message.windowTitle('Continue Gene Count Script')
        #     self.message.showMessage('Would you like to proceed?')
        #     self.message.continue_btn.setEnabled(True)
        #     self.message.exec_()
        #     self.message.activateWindow()
        return file_list

    def get_chromosomes_list(self, directory, tag, printio_handle):
        chromList = []
        # comment_filehandle = open(os.path.join(os.curdir, "Y2Hreadme.txt"), 'r')
        # except:
        #     text = '>>> ERROR <<<\n\nCannot find Y2Hreadme.txt file in Resources folder\n\nExecution Aborted!'
        #     self.message.windowTitle('ERROR!')
        #     self.message.continue_btn.setEnabled(False)
        #     self.message.showMessage(text)
        #     self.message.exec_()
        #     self.message.activateWindow()
        #     sys.exit()

        for chr_name in printio_handle.get_text_block_as_array(tag):
            chromList.append(chr_name.rstrip())
        return chromList

    def remove_file(self, directory, folder, file_list):
        for fi in file_list:
            os.remove(os.path.join(directory, folder, fi))
            sys.stdout.write(">>> Cleaned up file %s in folder %s\n" % (fi, folder))

    # def input_data_check(self, directory, input_data_folder, file_extenstion, folders=[]):
    #     self.check_path(directory, input_data_folder, 'Cannot find %s folder' % input_data_folder)
    #     if os.path.exists(os.path.join(directory, input_data_folder)):
    #         filecheck = self.get_file_list(directory, input_data_folder, file_extenstion)
    #         if len(filecheck) == 0:
    #             text = '>>> ERROR <<<\n\nThere appear to be no %s files in the folder %s to process' % (
    #                 input_data_folder, file_extenstion)
    #             self.message.windowTitle('ERROR!')
    #             self.message.continue_btn.setEnabled(False)
    #             self.message.showMessage(text)
    #             self.message.exec_()
    #             self.message.activateWindow()
    #             sys.exit()
    #
    #     if len(folders) > 0:
    #         if True in map(lambda x: os.path.exists(os.path.join(directory, x)), folders):
    #             text = ">>> WARNING:  Folders already exist! <<<\n\nThere might be old files in this " \
    #                     "folder.\nIf you continue the program will write over them!\n\n" \
    #                     ">>> RECOMMENDATION <<<\n\nPlease move the files and folder to a backup" \
    #                     "location"
    #             if self.prompt == 2:
    #                 self.message.windowTitle('Warning!')
    #                 self.message.continue_btn.setEnabled(True)
    #                 self.message.showMessage(text)
    #                 self.message.exec_()
    #                 self.message.activateWindow()
    #
    #         for f in folders:
    #             if not os.path.exists(os.path.join(directory, f)):
    #                 self.create_new_folder(directory, f)

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
        sys.stdout.write('>>> Converted  %d junctions in %s to a FASTA file.\n' % (counter, os.path.split(
                junctionFile)[-1]))
        sys.stdout.flush()


