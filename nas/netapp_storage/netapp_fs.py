import subprocess
import shlex

class Netapp(object):
	def __init__(self):
		pass

	def fs_chk(self,command):
		self.command = shlex.split(command)
		retcode = subprocess.Popen(self.command, stdout=subprocess.PIPE, universal_newlines=True).communicate()[0]
		return retcode
