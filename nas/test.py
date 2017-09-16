import os
import subprocess
import shlex

while True:
	command = input("Command: ")
	cmd = shlex.split(command)
	subprocess.call(cmd)
	if command == 'q': quit()
	print("Hello")
