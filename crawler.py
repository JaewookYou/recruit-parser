import json, requests, time, os
from arang import *
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from dbutil import * 
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def extract_image_sources(html):
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')

    if len(tables) < 2:
        print(f"[+] table is lower than 2")
        return [img['src'] for img in soup.find_all('img')]

    first_table = tables[0]
    second_table = tables[1]

    elements_between = first_table.find_all_next()[:-len(second_table.find_all_next())]

    image_sources = [img['src'] for img in elements_between if img.name == 'img']

    return image_sources

with open("config.json","r") as f:
    config = json.loads(f.read())

post_headers = config["post_headers"]
get_headers = config["get_headers"]

s = requests.session()
s.verify=False
#s.proxies = {"https":"http://192.168.20.17:8888"}

def crawl_dokchi():
    result = []
    board_number_list = []
    for channel in [175]:
        for i in range(1,4):
            article_list_url = f"https://cafe.naver.com/ArticleList.nhn?search.clubid=16996348&search.menuid={channel}&search.boardtype=L&search.page={i}"
            r = s.get(article_list_url, headers=get_headers)
            
            soup = BeautifulSoup(r.content, 'html.parser')

            board_numbers = soup.find_all('div', class_='board-number')

            t = [tag.get_text() for tag in board_numbers]
            board_number_list += t
    
    db = Database()

    articles = []

    for board_num in board_number_list:
        if not db.selectNum(board_num):
            print(f"[+] insert db - {board_num}")
            db.insertNum(board_num)
            articles.append(board_num)

    for article in articles:
        tdict = {}

        article_read_url = f"https://apis.naver.com/cafe-web/cafe-articleapi/v2.1/cafes/16996348/articles/{article}?query=&menuId=175&boardType=L&useCafeId=true&requestFrom=A"
        tdict['url'] = f"https://cafe.naver.com/dokchi/{article}"
        
        r = json.loads(s.get(article_read_url, headers=get_headers).content)["result"]["article"]
        
        tdict['subject'] = r["subject"].replace("\xa0","")
        print(f"[+] subject - {tdict['subject']}")

        content = r["contentHtml"].replace("\xa0","")
        imgsrcs = extract_image_sources(content)

        tdict['images'] = []

        for imgurl in imgsrcs:
            try:
                r = s.get(imgurl, headers=get_headers).content
                if not os.path.isdir("./images/"):
                    os.makedirs("./images/")
                ext = urlparse(imgurl).path.split("/")[-1].split(".")[-1]
                fname = f"./images/{he(os.urandom(16)).decode()}.{ext}"
                with open(fname, "wb+") as f:
                    f.write(r)
                tdict['images'].append(fname)
                print(f"[+] {fname} image save complete")
            except:
                print(f"[x] {imgurl}")
        
        time.sleep(1)
        result.append(tdict)
    
    return result

if __name__ == "__main__":
    crawl_dokchi()