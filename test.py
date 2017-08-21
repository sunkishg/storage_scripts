#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import required modules

import os
import re
import paramiko
import cmd
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")

netapp_filers = []
user_id = ""
pass_key = ""

Netapp_commands = ['system health status show', 'disk show -n', 'vol status -f', 'vol status -s', 'df -k', 'df -i']

outfile = 'Netapp_health_check_report.txt'
fhand = open(outfile, 'w')

fhand.write("Hi,\nThis is an automated Health check report for Netapp filers\n")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def nt_system_status(filer,command):
    try:
        ssh.connect(filer, username=user_id, password=pass_key)
    except:
        continue
    stdin, stdout, stderr = ssh.exec_command(command)
    stdin.flush()
    data = stdout.read()
    if re.search("ok", data):
        fhand.write("{0} Health status: OK\n".format(filer))
    else:
        fhand.write("{0} Health status: ATTN\n".format(filer))

def nt_broken_disk(filer,command):
    try:
        ssh.connect(filer, username=user_id, password=pass_key)
    except:
        continue
    stdin, stdout, stderr = ssh.exec_command(command)
    stdin.flush()
    data = stdout.read()
    if re.search("disk show: No unassigned disks"):
        fhand.write("{0} contains no unassigned disks\n".format(filer))
    else:
        fhand.write("{0} contains unassigned disks\n".format(filer))
        fhand.write("{0}\n".format(data))

def nt_fail_disk(filer,command):
    try:
        ssh.connect(filer, username=user_id, password=pass_key)
    except:
        continue
    stdin, stdout, stderr = ssh.exec_command(command)
    stdin.flush()
    data = stdout.read()
    if re.search("Broken disks (empty)", data):
        fhand.write("{0} contains no failed drives\n".format(filer))
    else:
        fhand.write("{0} contains failed drives\n".format(filer))
        fhand.write("{0}\n".format(data))

def nt_spare_disk(filer,command):
        try:
        ssh.connect(filer, username=user_id, password=pass_key)
    except:
        continue
    stdin, stdout, stderr = ssh.exec_command(command)
    stdin.flush()
    data = stdout.read()
    spare_count = 0
    for line in data.splitlines():
        if re.search("^spare", line):
            spare_count += 1
        else:
            continue
    else:
        fhand.write("{0} contains {1} spare disks\n".format(filer,spare_count))

def main():
    for filer in netapp_filers:
        nt_system_status(filer,Netapp_commands[0])
        nt_broken_disk(filer,Netapp_commands[1])
        nt_fail_disk(filer,Netapp_commands[2])
        nt_spare_disk(filer,Netapp_commands[3])


if __name__ == '__main__':
    main()
