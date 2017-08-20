#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import required modules

import os
import re
# import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import Encoders
from email.MIMEBase import MIMEBase
from datetime import datetime

# Today"s date
today = datetime.now().strftime("%Y-%m-%d")

# setup input/output files

# input files
source_file = "Filename"
source_fhand = open(source_file)

# output files
output_html = "filename"
html_fhand = open(output_html, "w")

output_csv = "filename"
csv_fhand = open(output_csv, "w")

# python data structures for data handling within the program
nas_fs = dict()


# Netapp function to retrieve volume info
def netapp(application, share_path, storage_array, storage_volume):
    # construct commands to be run
    netfscmd = "ssh storageops@{0} df -k {1}".format(storage_array, storage_volume)
    netindcmd = "ssh storageops@{0} df -i {1}".format(storage_array, storage_volume)

    # capture timestamp and execute commands
    time_now = datetime.now().strftime("%H:%M:%S")
    netfscmd_out = os.popen(netfscmd)
    netindcmd_out = os.popen(netindcmd)

    nas_fs[storage_volume] = {"date": today, "time": time_now, "array_type": "Netapp",
                              "application_name": application, "share": share_path, "array": storage_array,
                              "volume": storage_volume, "files": -1 }

    # parse commands output to construct report
    # netapp filesystem
    for fsline in netfscmd_out:
        fsdata = fsline.split()
        if re.search("snapshot", fsline) or re.search("snap reserve", fsline) or re.search("Filesystem", fsline) or len(
                fsdata) < 4: continue
        nas_fs[storage_volume]["total_space"] = "{0:.2f}".format(float(fsdata[1].split("KB")[0]) / (1024 * 1024))
        nas_fs[storage_volume]["used_space"] = "{0:.2f}".format(float(fsdata[2].split("KB")[0]) / (1024 * 1024))
        nas_fs[storage_volume]["avail_space"] = "{0:.2f}".format(float(fsdata[3].split("KB")[0]) / (1024 * 1024))
        nas_fs[storage_volume]["capacity"] = float(fsdata[4].split("%")[0])

    # netapp inodes
    for indline in netindcmd_out:
        inddata = indline.split()
        if re.search("Filesystem", indline) or len(inddata) < 3: continue
        nas_fs[storage_volume]["iused"] = inddata[1]
        nas_fs[storage_volume]["ifree"] = inddata[2]
        nas_fs[storage_volume]["itotal"] = int(inddata[1]) + int(inddata[2])
        nas_fs[storage_volume]["iused_cap"] = inddata[3].split("%")[0]     

def isilon(application, share_path, storage_array, storage_volume):
    # construct commands to be run
    isi_command = "ssh root@{0} '/usr/bin/isi quota quotas list --path={1} --format=csv --no-header --no-footer --verbose'".format(
        storage_array, storage_volume)

    # capture timestamp and execute commands
    time_now = datetime.now().strftime("%H:%M:%S")
    isi_command_out = os.popen(isi_command)

    # parse commands output to construct report
    nas_fs[storage_volume] = {"date": today, "time": time_now, "array_type": "isilon",
                              "application_name": application, "share": share_path, "array": storage_array,
                              "volume": storage_volume, "iused": -1, "ifree": -1, "iused_cap": -1, "itotal": -1}
    for isi_line in isi_command_out:
        isi_data = isi_line.split(",")
        if len(isi_data) < 10 or re.search('Type,AppliesTo,Path,Snap,Hard,Soft,Adv,Used', isi_line): continue
        nas_fs[storage_volume]["total_space"] = "{0:.2f}".format(float(isi_data[4]) / 1024 / 1024 / 1024)
        nas_fs[storage_volume]["used_space"] = "{0:.2f}".format(float(isi_data[10]) / 1024 / 1024 / 1024)
        nas_fs[storage_volume]["avail_space"] = "{0:.2f}".format(
            (float(nas_fs[storage_volume]["total_space"]) - float(nas_fs[storage_volume]["used_space"])))
        nas_fs[storage_volume]["capacity"] = "{0:.2f}".format(
            (float(nas_fs[storage_volume]["used_space"]) / float(nas_fs[storage_volume]["total_space"])) * 100)
        nas_fs[storage_volume]["files"] = isi_data[8]

def convert_csv():
    csv_fhand.write("Date,Time,File System,Application,Share Path,Storage Array,Storage Volume,Total Space (GB),Used Space (GB),Available Space (GB),% Space Used,Total Inodes,Used Inodes,Available Inodes,% File Capacity Used,Files\n")
    for key, value in sorted(nas_fs.items(), reverse=True):
        csv_fhand.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14},{15}\n".format(value['date'],value['time'],value['array_type'],value['application_name'],value['share'],value['array'],key,value['total_space'],value['used_space'],value['avail_space'],value['capacity'],value['itotal'],value['iused'],value['ifree'],value['iused_cap'],value['files']).replace("-1", " "))
        csv_fhand.flush()
    else:
        csv_fhand.close()

def convert_html():
        html_fhand.write("""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body {background-color: White ;}
    table {
            font-family: Calibri;
            border-collapse: collapse;
            width: 100%;
    }

    td, th {
            border: 1px solid Black;
            text-align: left;
            padding: 2px;
    }
    p.serif {
    font-family: "Times New Roman", Times, serif;
    }
    </style>
    </head>
    <body>
    <table>
    <caption><strong>NAS Filesystem Report</strong></caption>
    <thead>
    <tr>
    <th>Date</th>
    <th>Time</th>
    <th>FileSystem</th>
    <th>Application</th>
    <th>Share Path</th>
    <th>Storage Array</th>
    <th>Storage Volume</th>
    <th>Total Space (GB)</th>
    <th>Used Space (GB)</th>
    <th>Available Space (GB)</th>
    <th>Space Capacity Used</th>
    <th>Total Inodes</th>
    <th>Used Inodes</th>
    <th>Available Inodes</th>
    </th>File Capacity Used</th>
    <th>Files</th>
    </tr>
    </thead>
    """)
        for key, value in sorted(nas_fs.items(), reverse=True):
            # convert capacity % to a float value for html colour coding
            try:
                fscap = float(value["capacity"])
            except:
                fscap = -1
            try:
                icap = float(value["iused_cap"])
            except:
                icap = -1

            # add html colours as per capacity threshold
            if fscap >= 90:
                fscap = '<td bgcolor="#FF0000">{0}</td>'.format(fscap)
            elif fscap <= 89.99 and fscap >= 80:
                fscap = '<td bgcolor="#FFBF00">{0}</td>'.format(fscap)
            elif fscap <=79.99 and fscap >= 70:
                fscap = '<td bgcolor="#FFFF00">{0}</td>'.format(fscap)
            elif fscap == -1:
                fscap = '<td></td>'
            else:
                fscap = '<td bgcolor="#00FF00">{0}</td>'.format(fscap)

            if icap >= 90:
                icap = '<td bgcolor="#FF0000">{0}</td>'.format(icap)
            elif icap <= 89.99 and icap >= 80:
                icap = '<td bgcolor="#FFBF00">{0}</td>'.format(icap)
            elif icap <=79.99 and icap >= 70:
                icap = '<td bgcolor="#FFFF00">{0}</td>'.format(icap)
            elif icap == -1:
                icap = '<td></td>'
            else:
                icap = '<td bgcolor="#00FF00">{0}</td>'.format(icap)

            # write data to HTML File

            html_fhand.write('<tr>\n<td>{0}</td>\n<td>{1}</td>\n<td>{2}</td>\n<td>{3}</td>\n<td>{4}</td>\n<td>{5}</td>\n<td>{6}</td>\n<td>{7}</td>\n<td>{8}</td>\n<td>{9}</td>\n{10}\n<td>{11}</td>\n<td>{12}</td>\n<td>{13}</td>\n{14}\n<td>{15}</td>\n</tr>\n'.format(value['date'],value['time'],value['array_type'],value['application_name'],value['share'],value['array'],key,value['total_space'],value['used_space'],value['avail_space'], fscap, value['itotal'],value['iused'],value['ifree'],icap,value['files']).replace("-1", " "))
            html_fhand.flush()
        else:
            html_fhand.write("""</table>\n<br><br><br><p>This is an automated E-mail, for any assistance, please contact <a  href="mailto:email@domain.com">team name</a> (or) call to <span style="color:#cc6600;"> phone no </span> </p></body></html>""")
            html_fhand.close()


def send_email():
    with open(output_html) as myfile:
        myhtml = myfile.read()
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "NAS Filesystem Report: {0}".format(today)
    msg['From'] = "email@domain.com"
    msg['To'] = "email@domain.com"
    msg["Cc"] = "email@domain.com"
    # Create the body of the message (a plain-text and an HTML version).
    # text = "Automated NAS Storage Filesystem Report"
    html = "{0}".format(myhtml)
    mail_file = MIMEBase('application', 'csv')
    mail_file.set_payload(open('nas_fs_report.csv', 'rb').read())
    mail_file.add_header('Content-Disposition', 'attachment', filename='nas_fs_report.csv')
    Encoders.encode_base64(mail_file)
    msg.attach(mail_file)

    # Record the MIME types of both parts - text/plain and text/html.
    # part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    # msg.attach(part1)
    msg.attach(part2)
    # Send the message via local SMTP server.
    s = smtplib.SMTP('localhost')
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(msg["From"], msg["To"].split(",") + msg["Cc"].split(","), msg.as_string())
    s.quit()


def main():
    for csvrow in source_fhand:
        rowdata = csvrow.rstrip().split(",")
        if len(rowdata) < 4: continue
        application = rowdata[0]
        share_path = rowdata[1]
        storage_array = rowdata[2]
        storage_volume = rowdata[3]
        vendor = rowdata[4]
        if vendor == 'isilon':
            isilon(application, share_path, storage_array, storage_volume)
        elif vendor == 'netapp':
            netapp(application, share_path, storage_array, storage_volume)
    else:
        convert_csv()
        convert_html()
        send_email()

if __name__ == '__main__':
    main()

quit()
