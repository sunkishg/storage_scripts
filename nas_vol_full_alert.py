#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

netapp_filers = ['filer1', 'filer2']
isilon_clusters = ['filer1', 'filer2']

netapp_voluse_lst = list()
netapp_inodeuse_lst = list()
isilon_quota_lst = list()
out_file = 'nas_exceeded_volumes.html'
fhand = open(out_file, 'w')

time_now = datetime.now().strftime("%Y-%m-%d %H:%M")

def netvolspaceuse(filer):
    command = "ssh root@{0} df -h".format(filer)
    output = os.popen(command)
    for line in output:
        if re.search('snapshot', line) or re.search('snap reserve', line) or re.search('Filesystem', line) or len(line.split()) < 4 : continue
        use = line.split()[4].split('%')[0]
        if int(use) > 89:
            line_list = line.split()
            volume = line_list[0].split('/')[2]
            totalspace = line_list[1]
            usedspace = line_list[2]
            availablespace = line_list[3]
            capacity = line_list[4]
            netapp_voluse_lst.append('{0},{1},{2},{3},{4},{5}\n'.format(filer,volume,totalspace,usedspace,availablespace,capacity))

def netvolinodeuse(filer):
    command = "ssh root@{0} df -i".format(filer)
    output = os.popen(command)
    for line in output:
        if re.search('snapshot', line) or re.search('snap reserve', line) or re.search('Filesystem', line) or len(line.split()) < 4 : continue
        use = line.split()[3].split('%')[0]
        if int(use) > 89:
            line_list = line.split()
            volume = line_list[0].split('/')[2]
            iused = line_list[1]
            ifree = line_list[2]
            itotal = int(iused)+int(ifree)
            iusedper = line_list[3]
            netapp_inodeuse_lst.append('{0},{1},{2},{3},{4},{5}\n'.format(filer,volume,itotal,iused,ifree,iusedper))

def isilonexceededquota(cluster):
    command = "ssh root@{0} '/usr/bin/isi quota quotas list --exceeded --format=csv --no-header --no-footer'".format(cluster)
    output = os.popen(command)
    for line in output:
        data = line.split(",")
        if len(data) < 7 or re.search('Type,AppliesTo,Path,Snap,Hard,Soft,Adv,Used', line): continue
        path = data[2]
        hard_q = "{0:.2f}".format(int(data[4])/1024/1024/1024)
        used_q = "{0:.2f}".format(int(data[7])/1024/1024/1024)
        available_q = "{0:.2f}".format((float(hard_q) - float(used_q)))
        q_capacity = "{0:.2f}%".format((float(used_q)/float(hard_q))*100)
        isilon_quota_lst.append("{0},{1},{2},{3},{4},{5}".format(cluster,path,hard_q,used_q,available_q,q_capacity))

def convert_html():
    fhand.write("""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body {background-color: WhiteSmoke ;}
    table {
            font-family: Calibri, sans-serif;
            border-collapse: collapse;
            width: 75%;
    }
    
    td, th {
            border: 2px solid #778899;
            text-align: left;
            padding: 2px;
    }
    </style>
    </head>
    <body>
    <h2>Netapp Volumes space ussage exceeded 90% threshold value:</h2>
    <table>
    <tr>
            <th>Filer</th>
            <th>Volume</th>
            <th>Totoal Space</th>
            <th>Used Space</th>
            <th>Available Space</th>
            <th>Capacity</th>
    </tr>
    """)
    for line in netapp_voluse_lst:
        fhand.write("<tr>\n")
        for i in line.split(','):
            fhand.write("<td>{0}</td>\n".format(i))
        fhand.write("</tr>\n")
    fhand.write("</table>\n")
    fhand.flush()
    
    fhand.write("""
    <h2>Netapp Volumes Inode ussage exceeded 90% threshold value </h2>
    <table>
    <tr>
            <th>Filer</th>
            <th>Volume</th>
            <th>Totoal Inodes</th>
            <th>Used Inodes</th>
            <th>Available Inodes</th>
            <th>Capacity</th>
    </tr>
    """)
    for line in netapp_inodeuse_lst:
        fhand.write("<tr>\n")
        for i in line.split(','):
            fhand.write("<td>{0}</td>\n".format(i))
        fhand.write("</tr>\n")
    fhand.write("</table>\n")
    fhand.flush()

    fhand.write("""
        <h2>Isilon Disk quotas exceeded 90% threshold value</h2>
    <table>
    <tr>
            <th>Isilon Cluster</th>
            <th>Quota Path</th>
            <th>Total space(GBs)</th>
            <th>Used space(GBs)</th>
            <th>Available Space(GBs)</th>
            <th>Capacity</th>
    </tr>
    """)
    for line in isilon_quota_lst:
        fhand.write("<tr>\n")
        for i in line.split(','):
            fhand.write("<td>{0}</td>\n".format(i))
        fhand.write("</tr>\n")
    fhand.write("</table>\n")
    fhand.flush()

def send_email():
    with open(out_file) as myfile:
        myhtml = myfile.read()
    me = "email"
    you = "email"
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('multipart')
    msg['Subject'] = "Netapp and Isilon share disk quota exceeded Report: {0}".format(time_now)
    msg['From'] = me
    msg['To'] = you
    # Create the body of the message (a plain-text and an HTML version).
    text = "Automated Report: {0}\nNAS Volumes exceeded it's threshold value are mentioned below"
    html = "{0}".format(myhtml)
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    # Send the message via local SMTP server.
    s = smtplib.SMTP('localhost')
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(me, you, msg.as_string())
    s.quit()

for array in netapp_filers:
    try:
        netvolspaceuse(array)
        netvolinodeuse(array)
    except:
        print "Error while accessing {0}".format(array)

for array in isilon_clusters:
    try:
        isilonexceededquota(array)
    except:
        print "Error while accessing {0}".format(array)

convert_html()
send_email()

quit()
