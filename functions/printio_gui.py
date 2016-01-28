import sys, os

class printio():
    """Functions to print comments"""
    def __init__(self):
        pass
        # self.prompt = 0
        # self.message = m.Message_Dialog()
        # self.message.quit_btn.clicked.connect(self.message_quit_signal)
        # self.message.continue_btn.clicked.connect(self.message_continue_signal)

    # def message_quit_signal(self):
    #     self.message.hide()
    #     sys.exit()
    #
    # def message_continue_signal(self):
    #     self.message.hide()

    def print_centered(self, string):
        print
        if sys.stdout.isatty():
            if not os.popen('stty size', 'r').read():
                r, c = (100, 100)
            else:
                r, c = os.popen('stty size', 'r').read().split()
        else:
            r, c = (100, 100)
        for n in range(((int(c)+1)-len(string))/2):
            sys.stdout.write(' ')
        print string, "\n"

    def get_text_block(self, tag):
        found = False
        block = ''
        handle = open(os.path.join(os.curdir, "Y2Hreadme.txt"), 'r')
        for line in handle.readlines():
            if found:
                if line.strip() == ">>>END":
                    break
                block += line
            else:
                if line.strip() == ">>>" + tag:
                    found = True
        handle.close()
        return block

    def get_text_block_as_array(self, tag):
        found = False
        block = []
        handle = open(os.path.join(os.curdir, "Y2Hreadme.txt"), 'r')
        for line in handle.readlines():
            if found:
                if line.strip() == ">>>END":
                    break
                block.append(line.strip())
            else:
                if line.strip() == ">>>" + tag:
                    found = True
        handle.close()
        return block

    # def print_comment(self, tag):
    #     try:
    #         comment_filehandle = open(os.path.join(os.curdir, 'Y2Hreadme.txt'), 'r')
    #         text = self.get_text_block(comment_filehandle, tag)
    #         if self.prompt == 2:
    #             self.message.windowTitle('Message')
    #             self.message.showMessage("\n".join(text))
    #             self.message.exec_()
    #             self.message.activateWindow()
    #         comment_filehandle.close()
    #     except IOError:
    #         text = '>>> ERROR <<<\n\nCannot find Y2Hreadme.txt file in Resources folder\n\nExecution Aborted!'
    #         self.message.windowTitle('ERROR!')
    #         self.message.continue_btn.setEnabled(False)
    #         self.message.showMessage(text)
    #         self.message.exec_()
    #         self.message.activateWindow()
    #         sys.exit()

    # def show_message(self, text):
    #     self.message.windowTitle('Message')
    #     self.message.showMessage(text)
    #     self.message.exec_()
    #     self.message.activateWindow()

    def print_progress(self, infile, x, y, z, a):
        if a == 1:
            sys.stdout.write('>>> Processing {}:'.format(infile))
            sys.stdout.flush()
        if a == 2:
            sys.stdout.write('>>> Counting. {} sequences with blast hits in file: {}'.format(x, infile))
            sys.stdout.flush()
        if a == 3:
            sys.stdout.write('>>> Finished with file {}.\n{} sequences with blast hits.\n{} total hits in {} '
                             'minutes'.format(infile, x, y, z))
            sys.stdout.flush()
        if a == 4:
            sys.stdout.write('\t\n   1st sequence:  {}\n   2nd sequence:  {}\n   3rd sequence:  {}\n\n'.format(x, y, z))
            sys.stdout.flush()
