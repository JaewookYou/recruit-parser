import openai
import re
import json
import os

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)

with open(f"{script_dir}/config.json","r") as f:
    config = json.loads(f.read())
openai.api_key = config["openai_api_key"]

def find_last_number(string):
    numbers = re.findall(r'\d{1,3}', string)
    if not numbers:
        return None

    return int(numbers[-1])

def askgpt(ocrresult):
    with open("gptlog.txt", "a+") as f:
        mcontent = """지금부터 내가 보내는 채용공고를 ocr한 문구들을 보고 내가 취직하려는 직무와 회사가 맞는지 판단하려 해.
        이러한 정보를 바탕으로 앞으로 내가 보내는 OCR된 채용공고에서 어떤 직무를 뽑는지 보고서처럼 요약해줘
        요약할 땐 선발 방법에 대한건 별로 필요 없고, 직무와 전공이 어떤것인지가 제일 중요해.
        채용 분야나 직무가 화학공학, 환경 직무이거나 채용 대상이 화학공학, 환경, 고분자 관련 학과 졸업인지 봐줘
        또한 채용 대상이 대졸(학사)채용인지 고졸/전문대졸/초대졸 채용인지도 봐줘.
        해당하는 직무의 근무지역도 요약 정보에 포함해줘.
        적합 여부는 판단하지마.
        """
        
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": mcontent},
                {"role": "user", "content": ocrresult}
            ]
        )
        summary = completion.choices[0].message['content']
        f.write(f"```\n{summary}\n\n")
        #print(summary)
        result = {}
        result["summary"] = summary

        mcontent2 = """나는 대학 졸업(대졸)으로 화학공학, 환경 분야 직무로 취업을 준비하고 있어. 
        채용공고를 ocr한 문구의 요약본들로 내가 취직하려는 직무와 회사가 맞는지 판단하려 해.
        화학공학, 환경 직무와의 관련도를 고려해서 관련도를 1~100점 사이의 점수를 구해줘.
        채용 대상 혹은 자격이 대학(4년제 학사) 졸업이 아닌 경우 0점을 부여해줘.
        화학공학, 환경 관련 직무가 아닌경우 0점을 부여해줘.
        
        [점수 예시]
        0~40점 : 화학공학, 환경 직무와 관련성이 현저히 적거나 채용 대상이 대졸이 아님(고졸, 전문대졸, 초대졸 등)
        40~60점 : 화학공학, 환경 직무와 관련성이 적으나 판단이 살짝 어려움
        60점~79점 : 화학공학, 환경 직무와 관련성이 많아 보이나 판단이 살짝 어려움
        80점~100점 : 화학공학, 환경 직무와 관련성이 현저히 많음

        그 후 너가 대답할땐 설명이나 분석하지 말고 앞뒤말 다 빼고 관련도 점수를 숫자로만 말해줘.(ex. 30)
        """
        
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": mcontent2},
                {"role": "user", "content": summary}
            ]
        )
        content = completion.choices[0].message['content']
        f.write(f"점수 : {content}\n```\n\n--------------------------\n\n")
        print(f"점수 : {content}")
        result["score"] = find_last_number(content)
        return result

if __name__ == "__main__":
    askgpt("아아")

