import subprocess as sub
import threading
import shlex

class RunCmd(threading.Thread):
    def __init__(self, cmd, timeout):
        threading.Thread.__init__(self)
        self.cmd = shlex.split(cmd)
        self.timeout = timeout

    def run(self):
        try:
            self.p = sub.Popen(self.cmd, stdout=sub.PIPE, stderr=sub.PIPE, universal_newlines=True)
        except:
            self.p = None
        # RunCmd.out, RunCmd.err = self.p.communicate()


    def Run(self):
        self.start()
        self.join(self.timeout)

        if self.is_alive():
            # self.p.terminate()      #use self.p.kill() if process needs a kill
            self.p.kill()      #use self.p.terminate() if process needs a terminate
            self.join()
        
        if self.p != None:
            self.stdout, self.stderr = self.p.communicate()
            if self.p.returncode == 0:
                return self.p.returncode, self.stdout
            else:
                return self.p.returncode, self.stdout, self.stderr
        else:
            return 1,'unable to execute command!'

x = RunCmd("symcfg list", 60).Run()
print(x)
