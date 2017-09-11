#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import subprocess
import threading
import shlex


class Cmd(threading.Thread):
    """docstring"""

    def __init__(self, command, timeout=30):
        threading.Thread.__init__(self)
        self.command = shlex.split(command.strip())
        self.timeout = timeout

    def run(self):
        try:
            self.prcs = subprocess.Popen(self.command,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         universal_newlines=True)
            self.stdout, self.stderr = self.prcs.communicate()
        except Exception as e:
            self.prcs = None
            self.stderr = """unable to execute command!: {0}""".format(e)

    def runcmd(self):
        self.start()
        self.join(self.timeout)

        if self.is_alive():
            self.prcs.terminate()      #use self.prcs.kill() if process needs a kill
            # self.prcs.kill()      #use self.prcs.terminate() if process needs a terminate
            self.join()

        if self.prcs != None:
            command_response = {'return_code': self.prcs.returncode, 'stdout': self.stdout, 'stderr': self.stderr}
            return command_response
        else:
            command_response = {'return_code': 1, 'stdout': "", 'stderr': self.stderr }
            return command_response


def main():
    mycommand = input("Enter Command: ")
    myout = Cmd(mycommand).runcmd()
    print(myout)

if __name__ == '__main__':
    main()