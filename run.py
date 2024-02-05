from PIL import Image
import pytesseract
from crawler import *
from gptInterface import *
import smtplib, datetime, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

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



result = crawl_dokchi()
print(result)
resultText = ""

msg = MIMEMultipart(_subtype='mixed')
subject = datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d 채용공고 알림")
msg['Subject'] = subject

imgcnt = 0

for r in result:
    ocrtext = ""
    print(f"[+] ocr start - {r['subject']}")
    for image_path in r["images"]:
        image = Image.open(image_path)  
        ocrtext += pytesseract.image_to_string(image, lang='kor').replace(" ","")+"\n"
        with open('.'.join(image_path.split(".")[:-1])+".txt","w") as f:
            f.write(ocrtext)
        print(f"[+] ocr done - {len(ocrtext)}")

    text = f"""
    ```
    제목 : {r['subject']}
    공고(ocr) : {ocrtext[:10000]}
    ```
    """
    print(f"[+] ask gpt - {r['subject']}")
    with open(f"{script_dir}/gptlog.txt", "a+") as f:
        f.write(f"[+] ask gpt - {r['subject']}({r['url']})\n\n")
    gptresult = askgpt(text)
    score = gptresult["score"]
    
    if gptresult["score"] != None:
        if score >= 70:
            resultText += f"""<p>[!] 적합한 채용공고 발견!(관련도 {score}점)</p><br>
            <p>subject - {r['subject']}</p><br>
            <p>url - {r['url']}</p><br>
            <br>
            <p>{gptresult['summary']}</p><br>
            <br>
            <br>"""


            for image_path in r["images"]:
                resultText += f"""
                <img style="width: 800px;" src="cid:image{imgcnt}"><br>
                """
                
                with open(image_path, 'rb') as img_file:
                    img = MIMEImage(img_file.read(), _subtype=image_path.split(".")[-1], Name='gonggoimg')
                    img.add_header('Content-ID',f'<image{imgcnt}>')
                    msg.attach(img)

                imgcnt += 1
                 
            #print(resultText)
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

            

            
