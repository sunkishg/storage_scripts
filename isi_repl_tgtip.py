#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

mydict = dict()
lst = list()

#takes cluster name from user, use 'input' if python3
isiarray = raw_input("Enter Isilon Cluster Name: ").strip()
if len(isiarray) < 1 : quit()

#ssh to the cluser, get command output as a readfile
command = "ssh root@{0} '/usr/bin/isi sync policies list --format=csv --no-footer --no-header'".format(isiarray)
fhand = os.popen(command)

#creates a dict with uniq target IPs
for line in fhand:
    data = line.strip().split(",")[-1]
    if data not in mydict:
        mydict[data] = 1
    else:
        mydict[data] += 1

#conver dict into a list for sorting, use 'mydict.items()' method if python3
for key, val in list(mydict.iteritems()):
    lst.append((val, key))

lst.sort(reverse=True)
#prints output to the shell, use 'print()' function if python3
for key,val in lst:
    print "{0}: {1}".format(val,key)
