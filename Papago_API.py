import os
import sys
import urllib.request
from dotenv import load_dotenv
load_dotenv()
client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')

encText = urllib.parse.quote("반갑습니다") #encText는 이제 번역을 요구하는 것
data = "source=ko&target=en&text=" + encText
url = "https://openapi.naver.com/v1/papago/n2mt"
request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id",client_id)
request.add_header("X-Naver-Client-Secret",client_secret)
response = urllib.request.urlopen(request, data=data.encode("utf-8"))
rescode = response.getcode()
if(rescode==200):
    response_body = response.read()
    print(response_body.decode('utf-8'))
else:
    print("Error Code:" + rescode)

# 응답에 성공하면 결과값을 JSON 형식으로 반환한다
# srcLangType -> string -> 번역할 원본 언어의 언어 코드
# tarLangType -> string -> 번역한 목적 언어의 코드
# translatedText -> string -> 번역된 텍스트