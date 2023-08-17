import datetime
import requests
import os
import io
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from django.core.files import File
import hashlib

def to_date(date_str):
    # "8.3.목", "22.12.4.일" -> datetime.datetime
    current_year = datetime.datetime.now().year
    parts = date_str[:-2].split('.')  # 요일 부분을 제거하고 문자열을 분할합니다.

    # 연도 부분이 존재하지 않으면 현재 연도를 붙입니다.
    if len(parts) == 2:
        parts.insert(0, str(current_year)[2:])

    return datetime.datetime.strptime('.'.join(parts), "%y.%m.%d")

def get_at_most_three_photo_urls(media):
    """
    [
        {
            "type": "image",
            "thumbnail": "https://pup-review-ph..."
        }, 
        {
            "type": "video",
            "thumbnail": "https://video-phinf.psta..."
        }
    ]
    ->
    [
        "https://pup-review-ph..."
    ]
    """
    photo_urls = []

    for item in media:
        if item["type"] == "image":
            photo_urls.append(item["thumbnail"])

        if len(photo_urls) == 3:  # 최대 세 개의 사진 찾으면 중지
            break

    return photo_urls

def validate_image_stream(img_stream, max_size=1000000):
    original_img = Image.open(img_stream)
    
    # Remove any existing metadata (e.g., EXIF tags) from the image
    original_img = ImageOps.exif_transpose(original_img)
    
    buffer = io.BytesIO()
    
    quality = 100
    original_img.save(buffer, format="JPEG", quality=quality, optimize=True)
    while buffer.getbuffer().nbytes >= max_size and quality > 0:
        buffer = io.BytesIO()
        quality -= 10
        original_img.save(buffer, format="JPEG", quality=quality, optimize=True)
    
    buffer.seek(0)
    
    return ContentFile(buffer.read())

def compute_sha256(file_obj):
    # Create a new SHA256 hash object
    sha256 = hashlib.sha256()

    # Read the file in chunks and update the hash object
    for chunk in iter(lambda: file_obj.read(4096), b''):
        sha256.update(chunk)

    # Return the SHA256 hash as a hex string
    return sha256.hexdigest()

def download_img(url):
    response = requests.get(url)
    if response.status_code == 200:
        img_stream = io.BytesIO(response.content)
        
        image_sha256 = compute_sha256(img_stream)
        img_stream.seek(0)

        compressed_image = validate_image_stream(img_stream)
        
        result_file = File(compressed_image, name=image_sha256 + os.path.splitext(url)[1])
        return result_file
    else:
        # If the image is not downloaded successfully, return None or raise an exception
        return None


def to_time(time_str): 
        try: 
            return datetime.time(*map(int, time_str.split(':')))
        except Exception as e:
            return None
        
def to_day_of_week_eng(day_str):
    kor_eng = {
        '월': 'Mon', 
        '화': 'Tue', 
        '수': 'Wed', 
        '목': 'Thu', 
        '금': 'Fri', 
        '토': 'Sat', 
        '일': 'Sun'
    }
    day_str = next((k for k in kor_eng if (k in day_str)), None) # "화(8\u002F15)" -> "화"
    return kor_eng.get(day_str, None)

class NestedDictConverter:
    @staticmethod
    def _get_value_from_nested_dict(nested_dict, keys):
            ret = nested_dict
            for key in keys:
                try: 
                    ret = ret[key]
                except (KeyError, IndexError, TypeError):
                    return None
            return ret

    @staticmethod
    def convert_obj_by_rules(obj, rules):
        res = {}

        for key, rule in rules.items():
            val = obj
            if 'lookup' in rule:
                val = NestedDictConverter._get_value_from_nested_dict(obj, rule['lookup'])
            if 'post_apply' in rule:
                for func in rule['post_apply']:
                    try: 
                        val = func(val)
                    except Exception:
                        val = None

            res[key] = val

        return res

    @staticmethod
    def convert_list_by_rules(list, rules):
        res = []

        for obj in list:
            converted_obj = NestedDictConverter.convert_obj_by_rules(obj, rules)
            res.append(converted_obj)

        return res
    
def request_with_retry(url, max_retries=0, *args, **kwargs):
    for retry_count in range(max_retries):
        try:
            response = requests.get(url, *args, **kwargs)
            response.raise_for_status()  # 상태 코드가 400 이상인 경우 오류 발생
            return response
        
        except requests.exceptions.Timeout:
            print(f'Timeout on {url}. Retrying... ({retry_count + 1}/{max_retries})')
        
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while making the request: {e}")
            break  # Timeout 외 에러 발생 시 중단
    
    return None