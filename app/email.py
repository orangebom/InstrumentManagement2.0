import smtplib
import os
from email.mime.text import MIMEText
from threading import Thread
from flask import Flask, render_template


def send_async_email(msg,s):
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    s.quit()


def send_email(msg_to, subject, template, **kwargs):
    msg_from=os.environ.get('MAIL_USERNAME')
    passwd=os.environ.get('MAIL_PASSWORD') 

    content = render_template(template + '.html', **kwargs)
    msg = MIMEText(content,'html','utf-8')
    msg['Subject'] = subject
    msg['From'] = msg_from
    msg['To'] = msg_to
    msg["Accept-Language"]="zh-CN"
    msg["Accept-Charset"]="ISO-8859-1,utf-8"
    s = smtplib.SMTP_SSL("smtp.qq.com",465)
    s.login(msg_from, passwd)
    thr = Thread(target=send_async_email, args=[msg,s])
    thr.start()
    return thr
