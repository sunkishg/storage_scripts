#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import subprocess
import threading
import shlex

class Cmd(threading.Thread):
    """
    Execute the command using subprocess:
    :Usage: Cmd(Command,timeout=30) #default timeout value 30 seconds
    :param command: Full Command line as string
    :return: return code and the output =  of command or error
             if return code is different of 0 (error) the return is, return
             code, output =  and error output =
    """

    def __init__(self, command, timeout=600):
        threading.Thread.__init__(self)
        self.command = shlex.split(command.strip())
        self.timeout = timeout #default timeout time is 600 seconds ( 10 min )

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
    print(Cmd.__doc__)
    while True:
        print("type 'q' to quit!")
        mycmd = input("Enter Command: ").strip()
        subprocess.call('clear', shell=True)
        if mycmd == 'q': quit()

        output = Cmd(mycmd).runcmd()
        print(type(output))

if __name__ == '__main__':
    main()