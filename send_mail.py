from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import smtplib

time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
out_file = input("Enter Filename: ")
if len(out_file) < 1 : quit()
def send_email():
    with open(out_file) as myfile:
        myhtml = myfile.read()
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Filesystem Report: {0}".format(time_now)
    msg['From'] = "email@domain.com"
    msg['To'] = "groupemail@domain.com"
    msg["Cc"] = "manageremail@domain.com"
    # Create the body of the message (a plain-text and an HTML version).
    text = "Filesystem Report"
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

if __name__ == "__main__":
	send_email()
	print("Email sent!")
