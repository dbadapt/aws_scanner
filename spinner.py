# python class: Spinner
# Author: David Bennett - dbadapt@gmail.com
#
# display spinner on tty to the user knows something is
# happening.
#
# Usage:
#
# spinner = Spinner()
#
# for something in biglist: 
#   spinner.update()
#   { do something time consuming - don't print } 
# spinner.clear()
# { print something }

import sys

class Spinner(object):

    is_clear = True;
    offset = 0
    chars = ['|','/','-','\\']

    def update(self):
        if not sys.stdout.isatty():
            return;
        if not self.is_clear:
            sys.stdout.write('\b')
        sys.stdout.write(self.chars[self.offset])
        self.offset += 1
        if self.offset == len(self.chars):
            self.offset = 0;
        sys.stdout.flush()
        self.is_clear = False;

    def clear(self):
        if not sys.stdout.isatty():
            return;
        if not self.is_clear:
            sys.stdout.write('\b \b')
            sys.stdout.flush()
        self.is_clear = True;
             
