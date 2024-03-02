import smtplib, datetime, os, json, requests, re
from urllib.parse import urlparse, parse_qs
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import urllib3
from dbutil import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)

with open(f"{script_dir}/config.json","r") as f:
    config = json.loads(f.read())

print(config["smtptoid"])

def mailsend(original_msg):
    mailingList = config["smtptoid"]

    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls() 
    smtp.login(config["smtpid"], config["smtppw"])

    # 'msg' 객체를 복사하고 'To' 헤더를 설정합니다.
    msg['From'] = config["smtpid"]
    msg['To'] = ", ".join(mailingList)

    smtp.sendmail(config["smtpid"], mailingList, msg.as_string())

    smtp.quit()
    print(f'[+] mail send {msg["To"]} success')

if not os.path.isdir("./images/"):
    os.makedirs("./images/")


msg = MIMEMultipart(_subtype='mixed')
subject = datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d 채용공고 알림")
msg['Subject'] = subject
resultText = ""

imgcnt = 0

dutygroup = [187,188,189,190,191,192,193,229,230,231,233]

s = requests.session()
s.verify=False
s.proxies = {
    "http":"http://127.0.0.1:8888",
    "https":"http://127.0.0.1:8888"
}
s.headers = config["post_headers"]

db = Database()


u = "https://jasoseol.com/employment/calendar_list.json"
now = datetime.datetime.now()
starttime = datetime.datetime.strftime(now-datetime.timedelta(days=7),"%Y-%m-%dT15:00:00.000Z")
endtime = datetime.datetime.strftime(now+datetime.timedelta(days=7),"%Y-%m-%dT15:00:00.000Z")
data = {"start_time":starttime,"end_time":endtime}

r = s.post(u, json=data)
result = json.loads(r.content)

imgcnt = 0
for gonggo in result["employment"]:
    if gonggo["recruit_type"] != 0:
        continue
    if gonggo["business_size"] == "middle_market":
        continue
    go = False
    for employment in gonggo["employments"]:
        if employment["division"] not in [1,3]:
            continue
        for duty in employment["duty_groups"]:
            if duty["group_id"] in dutygroup:
                go = True
    if not go:
        continue

    gonggonum = gonggo["id"]
    
    if not db.selectNum(gonggonum):
        print(f"[+] insert db - {gonggonum}")
        db.insertNum(gonggonum)
    else:
        continue

    name = gonggo["name"]
    title = gonggo["title"]

    resultText += f"{name} {title}<br>"
    
    u2 = "https://jasoseol.com/employment/get.json"
    data = {"employment_company_id":gonggonum}

    r = json.loads(s.post(u2, json=data).content)
    emp_page_url = r["employment_page_url"]
    
    resultText += f"지원링크 - {emp_page_url}<br>"

    url_pattern = r'src="(https?://[^"]+)"'
    imageurls = re.findall(url_pattern, r["content"])
    
    emp_images = []
    
    for imageurl in imageurls:
        ext = urlparse(imageurl).path.split("/")[-1].split(".")[-1]
        imagecontent = requests.get(imageurl, verify=False).content

        resultText += f"""
        <img style="width:800px;" src="cid:image{imgcnt}"><br>
        """
        
        img = MIMEImage(imagecontent, _subtype=ext, Name='gonggoimg')
        img.add_header('Content-ID',f'<image{imgcnt}>')
        msg.attach(img)

        imgcnt += 1



with open(f"{script_dir}/result.txt", "a+") as f:
    f.write(resultText)
            
if resultText != "":
    print("[+] mail send")    
    html = f"""
    <!doctype html>
    <html>
        <body>
            {resultText}
        </body>
    </html>
    """
    html_body = MIMEText(html, 'html')
    msg.attach(html_body)

    mailsend(msg)

            

            
