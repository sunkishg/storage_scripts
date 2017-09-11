#!/usr/bin/python
# -*- coding: utf-8 -*-

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import xml.etree.ElementTree as ET
import os
import smtplib

time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
mydict = dict()
outfile = 'outfile.html'
fhand = open(outfile, 'w')

def symcfglist():
    command = "symcfg list -output xml_e"
    symout = os.popen(command)
    stuff = ET.fromstring(symout.read())
    arrays = stuff.findall('Symmetrix/Symm_Info')
    arraylst = list()
    for item in arrays:
        arraylst.append(item.find('symid').text)
    return arraylst

def list_logins(array):
    wwn_list = list()
    uniqwwn_data = list()
    command = "symaccess -sid {0} list logins -output xml_e".format(array)
    symlistlogins = os.popen(command)
    stuff = ET.fromstring(symlistlogins.read())
    originator_port_wwn_lst = stuff.findall('Symmetrix/Devmask_Login_Record/Login')
    for wwn in originator_port_wwn_lst:
        logged_in = wwn.find('logged_in').text
        on_fabric = wwn.find('on_fabric').text
        if logged_in == 'No' and on_fabric == 'Yes':
            originator_port_wwn = wwn.find('originator_port_wwn').text
            wwn_list.append(originator_port_wwn)
    for port_wwn in set(wwn_list):
        command = "symaccess -sid {0} list -type initiator -wwn {1} -output xml_e".format(array,port_wwn)
        wwnigout = os.popen(command)
        stuff = ET.fromstring(wwnigout.read())
        group_name_lst = stuff.findall('Symmetrix/Initiator_Group/Group_Info')
        for item in group_name_lst:
            ig_group_name = item.find('group_name').text
            uniqwwn_data.append("{0},{1}".format(port_wwn,ig_group_name))
    mydict[array] = uniqwwn_data

def convert_html():
    fhand.write("""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
        table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        }
        th, td {
        padding: 1px;
        text-align: left;
        }
        </style>
        </head>
        <body>
        <h2>EMC Symmetrix VMAX: Host WWNS that not logged into the array:</h2>
        """)
    for array,value in mydict.iteritems():
        if len(value) > 0:
            fhand.write('<h4>Symmetrix Array: {0}</h4>\n'.format(array))
            fhand.write('<table style="width:40%">\n<thead>\n<th>Host WWN</th>\n<th>Host IG Group</th>\n</thead>\n')
            for item in value:
                data = item.split(',')
                if len(data) > 1:
                    fhand.write('<tr>\n<td>{0}</td>\n<td>{1}</td>\n</tr>\n'.format(data[0],data[1]))
                else:
                    continue
            else:
                fhand.write('</table>\n<br>\n<br>\n<br>\n')
                fhand.flush()
    else:
        fhand.write('</body>\n</html>')
        fhand.flush()

def send_email():
    with open(outfile) as myfile:
        myhtml = myfile.read()
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "EMC Symmetrix List Logins: {0}".format(time_now)
    msg['From'] = "e-mail id"
    msg['To'] = "e-mail id"
    msg["Cc"] = "e-mail id"
    # Create the body of the message (a plain-text and an HTML version).
    text = "Automated EMC Symmetrix List Logins Report"
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
    s.sendmail(msg["From"], msg["To"].split(",") + msg["Cc"].split(","), msg.as_string())
    s.quit()

symcfglist = symcfglist()

for array in symcfglist:
    try:
        list_logins(array)
    except Exception as error:
        print("Unable to Run commands on Symmetrix Array: {0}\n Error:{1}".format(array, error))
else:
    convert_html()
    send_email()
