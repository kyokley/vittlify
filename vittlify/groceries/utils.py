# Based on an example from http://masnun.com/2010/01/01/sending-mail-via-postfix-a-perfect-python-example.html
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import os
from config.settings import EMAIL_FROM_ADDR

def sendMail(to_addr, subject, text, from_addr=EMAIL_FROM_ADDR, files=None, server='localhost'):
    if type(to_addr) is not list:
        to_addr = [to_addr]
    if not files:
        files = []
    if type(files) is not list:
        files = [files]

    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = COMMASPACE.join(to_addr)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for file in files:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(file, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="%s"' % os.path.basename(file))
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(from_addr, to_addr, msg.as_string())
    smtp.close()

def queryDictToDict(data):
    ret = dict()
    for key, val in data.items():
        ret[key] = val

    return ret
