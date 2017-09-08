#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import subprocess
from run_command import Cmd

while True:
    print("type 'quit' to quit!")
    mycmd = input("Enter Command: ").strip()
    subprocess.call('clear', shell=True)
    if mycmd == 'quit': quit()

    output = Cmd(mycmd).Run()
    if output[0] == 0:
        print(output[1])
    else:
        print("Error: {0}".format(output[-1]))
