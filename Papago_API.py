import os
import urllib.parse
import urllib.request
from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')

def translate_and_extract(word):
    encText = urllib.parse.quote(word)  # encText는 번역 요청 텍스트
    data = "source=ko&target=en&text=" + encText
    url = "https://openapi.naver.com/v1/papago/n2mt"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()

    if rescode == 200:
        response_body = response.read().decode('utf-8')
        translated_text = extract_translated_text(response_body)
        if translated_text:
            return(translated_text)
        else:
            return f"Translated text not found."
    else:
        return f"Error Code: {rescode}"

def extract_translated_text(json_response):
    # "translatedText" 문자열 찾기
    translated_text_index = json_response.find('"translatedText":"')
    if translated_text_index != -1:
        start_index = translated_text_index + len('"translatedText":"')
        end_index = json_response.find('"', start_index)
        if end_index != -1:
            translated_text = json_response[start_index:end_index]
            return translated_text
    return None
