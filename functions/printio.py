import sys, os
from libraries.termcolor import colored, cprint


class printio():
    """Functions to print comments"""
    def __init__(self):
        self.print_grey_on_cyan = lambda x: cprint(x, 'grey', 'on_cyan')
        self.print_grey_on_red = lambda x: cprint(x, 'grey', 'on_red')
        self.print_grey_on_yellow = lambda x: cprint(x, 'grey', 'on_yellow')
        self.print_magenta = lambda x: cprint(x, 'magenta')
        self.print_red = lambda x: cprint(x, 'red')
        self.print_yellow = lambda x: cprint(x, 'yellow')

    def print_centered(self, string):
        r = 0
        c = 0
        print
        if sys.stdout.isatty():
            if not os.popen('stty size', 'r').read():
                r, c = (100, 100)
            else:
                r, c = os.popen('stty size', 'r').read().split()
        else:
            r, c = (100,100)
        for n in range(((int(c)+1)-len(string))/2):
            sys.stdout.write(' ')
        print (colored(string, 'red', attrs=['bold']))
        print 

    def get_raw_input(self, string='\nType Y when you are ready to proceed, or N to abort: ', list=['y', 'Y', 'n', 'N']):
        cprint(string, 'white', attrs=['dark'])
        a = ''
        while True:
            a = raw_input()
            if a not in list:
                continue
            else:
                break
        return a

    def get_text_block(self, handle, tag):
        found = False
        block = []
        for line in handle:
            if found:
                if line.strip() == ">>>END": break
                block.append(line.rstrip())
            else:
                if line.strip() == ">>>" + tag:
                    found = True
        return block

    def print_comment(self, tag):
        try:
            comment_filehandle = open(os.path.join(os.curdir, 'Resources', 'Y2Hreadme.txt'), 'r')
        except IOError:
            print (colored('ERROR: Cannot fine the Y2Hreadme.txt file in Resources folder', 'red'))
            print '    Execution Aborted!'
            exit()
        text = self.get_text_block(comment_filehandle, tag)
        sys.stdout.write(colored("\n".join(text), 'cyan'))
        # print "\n".join(text)
        comment_filehandle.close()

    def print_progress(self, infile, x, y, z, a):
        if a == 1:
            self.print_yellow('\nProcessing {}:' .format(infile))
        if a == 2:
            self.print_yellow('Counting. {} sequences with blast hits in file: {}' .format(x, infile))
        if a == 3:
            self.print_yellow('\nFinished with file {}. {} sequences with blast hits. {} total hits in {} minutes' .format(infile, x, y, z))
        if a == 4:
            self.print_magenta('1st sequence:  {}'.format(x))
            self.print_magenta('2nd sequence:  {}'.format(y))
            self.print_magenta('3rd sequence:  {}'.format(z))
