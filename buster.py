# coding utf-8
import requests
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pdb

import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

FROM_ADDRESS = 'xxxx'
MY_PASSWORD = 'xxxx'
BCC=""
SUBJECT = 'GmailのSMTPサーバ経由'
BODY = 'pythonでメール送信'


def create_message(from_addr, to_addr, bcc_addrs, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Bcc'] = bcc_addrs
    msg['Date'] = formatdate()
    return msg


def send_mail(from_addr, to_addrs, msg):
    smtpobj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpobj.ehlo()
    smtpobj.starttls()
    smtpobj.ehlo()
    smtpobj.login(FROM_ADDRESS, MY_PASSWORD)
    smtpobj.sendmail(from_addr, to_addrs, msg.as_string())
    smtpobj.close()

f = open(r"userlist.txt","r")
ftext = f.read()
lines = re.split("[\r\n]",ftext)
i=0
j=0
userlist=[]
check_list=[]
for line in lines:
    sections = re.split(",",line)
    userlist.append([])
    j = 0
    for section in sections:
        if section != "":
            userlist[i].append(section)
            if (j == 1 and userlist[i][j] == '0'):
                check_list.append(userlist[i][0])
            j=j+1
    i=i+1
f.close()

def send_alarm(username, fake_user, url):
    for user in userlist:
        if username == user[0]:
            mailaddr = user[2]
            break
    subject = "【提醒】您的微博账号疑似被高仿"
    body = "您的微博账号@"+username+"疑似被高仿，\n高仿的id为@"+fake_user+"，\n高仿账号主页地址："+url
    msg = create_message(FROM_ADDRESS, mailaddr, BCC, subject, body)
    send_mail(FROM_ADDRESS, mailaddr, msg)
    print("mail sent")

def process(uid_link,username,fake_user):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    url = "https:"+uid_link+"?is_all=1"
    driver.get("https:"+uid_link+"?is_all=1")

    time.sleep(10)

    user_home = driver.page_source

    head_weibo_result = re.search("WB_text W_f14.*[\n\r]*(.*)</div>",user_home)
    if head_weibo_result  is None:
        return 0
    weibo_txt = head_weibo_result.group(1)
    fake_msg = re.search("漫.*游|国.*际|重新.*关注", weibo_txt)
    if fake_msg is not None:
        print(weibo_txt)
        send_alarm(username, fake_user, url)
        return 1
    else:
        return 0


headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"}




# while True:
#     if int(time.time())%60 == 0:
for username in check_list:
    url='https://s.weibo.com/user?q='+username+'&Refer=weibo_user'
    response = requests.get(
            url,
            headers=headers)
        #レスポンスオブジェクトのjsonメソッドを使うと、
        #JSONデータをPythonの辞書オブジェクトを変換して取得できる。
    page =response.text

    # pattern = re.compile(r"""a href="(//weibo.com/u/[0-9]+)".*user_name">[-_]{0,2}<em class="s-color-red">"""+username+"""</em>[-_]{0,2}</a>"""))
    pattern = re.compile(r"""a href="(//weibo.com/u/[0-9]+)".*user_name">(.*)</a>""")
    result = pattern.finditer(page)

    for i in result:
        fake_user_raw = i.group(2)
        fake_user = re.sub("<[^>]*>","",fake_user_raw)
        fake_pattern = ["-"+username, "_"+username, username+"-", username+"_"]

        if fake_user in fake_pattern:
            print(fake_user)
            ret = process(i.group(1), username, fake_user)
            if ret == 1:
                check_list.remove(username)
                for user in userlist:
                    if user[0] == username:
                        user[1] == '1'
                        user.append(fake_user)
                        break
                f = open("userlist.txt","w")
                for user in userlist:
                    for section in user:
                        f.write(section+',')
                    f.write('\n')
                f.close()
