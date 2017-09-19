#!/usr/bin/env python
# -*- coding: utf-8 -*-
#title           :isilon_exceeded_disk_quotas_chk.py
#description     :This script will gather disk quota information from Isilon arrays and reports disk quotas exceeded defined threshold value
#author          :Govardhan
#date            :20170825
#version         :1.2
#usage           :python isilon_exceeded_disk_quotas_chk.py
#notes           :
#python_version  :2.6.9
__author__ = "Govardhan Sunkishela"
__copyright__ = "Copyright 2017, NAS Project"
__credits__ = ["Bandaru S"]
__license__ = "OPEN"
__version__ = "1.0.1"
__maintainer__ = "Govardhan"
__email__ = "rob@spot.colorado.edu"
__status__ = "Production"
#==============================================================================

# Import the modules needed to run the script.
import os
import json
import math
import smtplib
import sqlite3
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import Encoders
from email.MIMEBase import MIMEBase
from datetime import datetime

# Today"s date
start_time = time.time()
today = datetime.now().strftime("%Y-%m-%d")

# setup input/output files
# input
isilon_clusters = {
    'cluster_name': 'isilon', \
}

# process
nas_fs = list()
exceeded_share_count = 0
threshold_value = 90

# output
out_file = 'Isilon_exceeded_disk_quotas.html'
fhand = open(out_file, 'w')

output_csv = "Isilon_exceeded_disk_quotas.csv"
csv_fhand = open(output_csv, "w")
# create and connect to database
conn = sqlite3.connect('isilon_exceeded_disk_quotas.sqlite')
cur = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS isilon_cluster;
DROP TABLE IF EXISTS isilon_quota_info;

CREATE TABLE IF NOT EXISTS isilon_cluster (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    cluster_name TEXT UNIQUE
);
CREATE TABLE IF NOT EXISTS isilon_quota_info (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    cluster_id INTEGER,
    quota_path TEXT,
    hard_quota REAL,
    advisory_quota REAL,
    usage_derived REAL,
    available_space REAL,
    filesystem_capacity REAL
);
""")

def convert_bytesto(bytes, to='g', bsize=1024):
    # convert bytes to MB, GB, TB etc.
    system_units = {'k': 1, 'm': 2, 'g': 3, 't': 4, 'p': 5, 'e': 6}

    try:
        mybyte = float(bytes)
    except:
        mybyte = 0

    outsize = math.ceil((mybyte / (bsize ** system_units[to])) *100) / 100
    return (outsize)

def isilon_disk_quotas(array):

    # update isilon_clusters table with the array info
    cur.execute('''INSERT OR IGNORE INTO isilon_cluster (cluster_name)
        VALUES (:array)''', {'array': array} )
    cur.execute('SELECT id FROM isilon_cluster WHERE cluster_name =:array ', {'array': array})
    cluster_id = cur.fetchone()[0]

    # command
    quota_cmd = "ssh root@{0} '/usr/bin/isi quota quotas list --format=json'".format(array)

    # execute
    quota_output = os.popen(quota_cmd)
    quota_data = quota_output.read()

    try:
        quota_jsondump = json.loads(quota_data)
    except:
        quota_jsondump = None

    if quota_jsondump is not None:
        for quota_line in quota_jsondump:
            # advance if path not given
            quota_path = quota_line['path']
            if quota_path == None: continue

            # convert values to floating numbers with 2 decimal places
            hard_quota = convert_bytesto(quota_line["thresholds"]['hard'])
            advisory_quota = convert_bytesto(quota_line["thresholds"]['advisory'])
            usage_derived = convert_bytesto(quota_line["usage_derived"])
            available_space = math.ceil((hard_quota - usage_derived) *100) / 100
            filesystem_capacity = math.ceil(((usage_derived / hard_quota) * 100) * 100) / 100

            # update isilon_quota_info table with the filesystem info
            cur.execute('''INSERT OR REPLACE INTO isilon_quota_info (cluster_id, quota_path, hard_quota, advisory_quota, usage_derived, available_space, filesystem_capacity)
                VALUES (:cluster_id, :quota_path, :hard_quota, :advisory_quota, :usage_derived, :available_space, :filesystem_capacity)''',
                {'cluster_id': cluster_id, 'quota_path': quota_path, 'hard_quota': hard_quota, 'advisory_quota': advisory_quota, 'usage_derived': usage_derived, 'available_space': available_space, 'filesystem_capacity': filesystem_capacity})
            conn.commit()

def read_from_sql():
    global threshold_value
    cur.execute('''SELECT isilon_cluster.cluster_name, isilon_quota_info.quota_path, isilon_quota_info.hard_quota, isilon_quota_info.advisory_quota, isilon_quota_info.usage_derived, isilon_quota_info.available_space, isilon_quota_info.filesystem_capacity
        FROM isilon_quota_info JOIN isilon_cluster
        ON isilon_quota_info.cluster_id = isilon_cluster.id
        WHERE isilon_quota_info.filesystem_capacity > {0} ORDER BY isilon_quota_info.cluster_id, isilon_quota_info.quota_path
'''.format(threshold_value))
    sql_read_data = cur.fetchall()
    return sql_read_data

def convert_csv():
    csv_fhand.write("Isilon Cluster,Quota Path,Hard Quota (GBs),Advisory Quota(GBs),Used Quota(GBs),Available Quota(GBs),Capacity Used%\n")
    csv_raw_data = read_from_sql()
    for x in csv_raw_data:
        if len(x) < 6: continue
        csv_fhand.write("{0},{1},{2},{3},{4},{5},{6}\n".format(x[0],x[1],x[2],x[3],x[4],x[5],x[6]))
        csv_fhand.flush()
    else:
        csv_fhand.close()

def convert_html():
    global exceeded_share_count # Global variable for counting no of shares
    global threshold_value
    html_data = read_from_sql()
    exceeded_share_count = len(html_data)
    if exceeded_share_count > 0:
        fhand.write("""
<!DOCTYPE html>
<html>
<head>
<style>
body {background-color: White ;}
table {
        font-family: Calibri;
        border-collapse: collapse;
        width: 80%;
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
<body>""")
        fhand.write('<h3 style="color:blue;font-family:verdana;">Total <mark><i>"{0}"</i></mark> Isilon disk quotas exceeded {1}% threshold Value</h3>'.format(exceeded_share_count, threshold_value))
        fhand.write('<table>\n<thead>\n<tr>\n<th>Isilon Cluster</th>\n<th>Quota Path</th>\n<th>Hard Quota (GBs)</th>\n<th>Advisory Quota(GBs)</th>\n<th>Used Quota(GBs)</th>\n<th>Available Quota(GBs)</th>\n<th>Capacity Used%</th>\n</tr>\n</thead>\n')
        for html_line in html_data:
            fscap = html_line[-1]
            if fscap >= 98:
                fscap = '<td bgcolor="#FF4136">{0}</td>'.format(fscap) #RED
            elif fscap <= 97.99 and fscap >= 95:
                fscap = '<td bgcolor="#FF851B">{0}</td>'.format(fscap) #ORANGE
            elif fscap <= 95.99 and fscap >= 90:
                fscap = '<td bgcolor="#e0ffff">{0}</td>'.format(fscap) #lightcyan
            else:
                fscap = '<td bgcolor="#01FF70">{0}</td>'.format(fscap) #LIME
            # write data to HTML File
            fhand.write('<tr>\n<td>{0}</td>\n<td>{1}</td>\n<td>{2}</td>\n<td>{3}</td>\n<td>{4}</td>\n<td>{5}</td>\n{6}\n</tr>'.format(html_line[0],html_line[1],html_line[2],html_line[3],html_line[4],html_line[5],fscap))
            fhand.flush()
        else:
            fhand.write("""</table>\n<br><br><br><i><p style="color:#111111;font-family:verdana;font-size:80%;">Script runtime: "{0:.2f}" Seconds<br><br>This is an automated report generated from host "Hostname"<br><br>Thank you,<br><b><a  style="color:#0074D9;" href="mailto:E-mail">Name</a></b><br>Contact:<b><span style="color:#FF4136;"> Number </span></b> </p></i><br><br></body></html>""".format(time.time() - start_time))
            fhand.close()

def send_mail():
    with open(out_file) as myfile:
        myhtml = myfile.read()
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Isilon disk quota exceeded Report: {0}".format(today)
    msg['From'] = "email@domain.com"
    msg['To'] = "email@domain.com"
    msg["Cc"] = "email@domain.com"
    # Create the body of the message (a plain-text and an HTML version).
    html = "{0}".format(myhtml)
    mail_file = MIMEBase('application', 'csv')
    mail_file.set_payload(open('Isilon_exceeded_disk_quotas.csv', 'rb').read())
    mail_file.add_header('Content-Disposition', 'attachment', filename='Isilon_exceeded_disk_quotas.csv')
    Encoders.encode_base64(mail_file)
    msg.attach(mail_file)
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(html, 'html')
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    # Send the message via local SMTP server.
    s = smtplib.SMTP('localhost')
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    s.sendmail(msg["From"], msg["To"].split(",") + msg["Cc"].split(","), msg.as_string())
    s.quit()

def main():
    for array,vendor in sorted(isilon_clusters.iteritems()):
        if vendor == 'isilon':
            isilon_disk_quotas(array)
    else:
        convert_csv()
        convert_html()
        send_mail()

if __name__ == '__main__':
    main()
    cur.close()
    conn.close()
quit()
