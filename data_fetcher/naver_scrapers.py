import json

from django.utils import timezone

import requests
from bs4 import BeautifulSoup

from .utils import (request_with_retry, 
                    to_date, 
                    to_time, 
                    to_day_of_week_eng, 
                    get_at_most_three_photo_urls, 
                    download_img, 
                    NestedDictConverter, 
                    )

class NaverScraper:
    list_params = {
        'query': None, 
        'page': 1, 
        'displayCount': 75, 
        'type': 'SITE_1', 
        'sm': 'clk', 
        'style': 'v5'
    }
    list_url = 'https://m.map.naver.com/search2/searchMore.naver'

    list_result_conversion = {
        # 'NAVER KEY': 'OUR KEY'
        'id': 'place_id', 
        'category': 'categories', 
        'roadAddress': 'address', 
        'thumUrl': 'image_url', 
        'y': 'latitude', 
        'x': 'longitude', 
        'naverBookingUrl': 'reservation_link'
    }

    detail_url = "https://m.place.naver.com/restaurant/%s/home"

    def get_keywords(self, place_obj):
        restaurant_base_key = next((k for k in place_obj if 'RestaurantBase' in k), None)
        if not restaurant_base_key:
            return None
        
        keywords = place_obj[restaurant_base_key]['keywords']

        return {
            'keywords': keywords
        }
    
    
    
    open_hours_conversion_rules = {
        'day': {
            'lookup': ['day'], 
            'post_apply': [to_day_of_week_eng]
        },
        'open_time': {
            'lookup': ['businessHours', 'start'],
            'post_apply': [to_time]
        },
        'close_time': {
            'lookup': ['businessHours', 'end'],
            'post_apply': [to_time]
        },
        'last_order_time': {
            'lookup': ['lastOrderTimes', 0, 'time'],
            'post_apply': [to_time]
        },
        'break_start_time': {
            'lookup': ['breakHours', 0, 'start'],
            'post_apply': [to_time]
        },
        'break_end_time': {
            'lookup': ['breakHours', 0, 'end'],
            'post_apply': [to_time]
        },
    }

    

    def get_open_hours(self, place_obj):
        root_query_key = next((k for k in place_obj if 'ROOT_QUERY' in k), None)
        if not root_query_key:
            return None
        
        root_query_obj = place_obj[root_query_key]
        restaurant_key = next((k for k in root_query_obj if k.startswith('restaurant')), None)
        if not restaurant_key:
            return None
        
        try:
            business_hours = root_query_obj[restaurant_key]['newBusinessHours'][0]['businessHours']
        except (IndexError, TypeError, KeyError): 
            print(f'Unable to get business hours')
            return None
        
        open_hours = NestedDictConverter.convert_list_by_rules(business_hours, self.open_hours_conversion_rules)
        
        open_hours = [day for day in open_hours if day['open_time'] != None]

        return {
            'open_hours': open_hours
        }

    menu_conversion_rules = {
        'name': {
            'lookup': ['name'], 
        },
        'image_url': {
            'lookup': ['images', 0], 
        },
        'price': {
            'lookup': ['price']
        }, 
        'description': {
            'lookup': ['description']
        }
    }

    def get_menu(self, place_obj):
        menu_keys = [k for k in place_obj if k.startswith('Menu:')]
        if not menu_keys:
            return None
        
        menus = [place_obj.get(key) for key in menu_keys]

        converted_menus = NestedDictConverter.convert_list_by_rules(menus, self.menu_conversion_rules)
        return {
            'menu': converted_menus
        }

    detail_result_conversion_handlers = [
        get_keywords, 
        get_open_hours, 
        get_menu
    ]

    def scrape_details(self, place_id):
        print(f'called: scrape_details({place_id})')
        url = self.detail_url % place_id
        
        response = request_with_retry(url, max_retries=3)
        if response is None:
            return None

        page = BeautifulSoup(response.content, 'html.parser')
        script_tags = page.find('body').find_all('script')
        if (len(script_tags) < 3 or script_tags[2].string is None):
            print('unexpected html structure')
            return None
        
        content = script_tags[2].string
        start_target = 'window.__APOLLO_STATE__ = '
        end_target = '\n'
        start_idx = content.find(start_target) + len(start_target)
        end_idx = content.find(end_target, start_idx)

        place_obj = content[start_idx:end_idx].removesuffix(';')
        place_obj = json.loads(place_obj)

        res = {}
        for handler in self.detail_result_conversion_handlers:
            place_info = handler(self, place_obj)
            if place_info is None:
                continue
            
            res.update(place_info)

        return res

    def search_place(self, query):
        print(f'called: search_place({query})')

        url = self.list_url
        params = self.list_params
        params['query'] = query

        response = request_with_retry(url, max_retries=3, params=params, timeout=5)

        try: 
            place = response.json()['result']['site']['list'][0]
        except (AttributeError, requests.exceptions.JSONDecodeError, KeyError, IndexError) as e:
            print(f'Search failed on query: {query}')
            print(e)
            return None
        
        res = {}

        for (naver_key, key) in self.list_result_conversion.items():
            res[key] = place[naver_key]
            if naver_key == 'id': 
                res[key] = res[key][1:] # drop first letter
            
        return res
    
    review_url = 'https://api.place.naver.com/graphql'
    review_headers = {
        "Content-Type": "application/json",
        "Host": "api.place.naver.com",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/115.0.0.0"
    }

    def scrape_likes(self, place_id):
        try: 
            request_data = {
                "operationName": "getVisitorReviewStats",
                "query": "query getVisitorReviewStats($id: String, $businessType: String = \"place\") {visitorReviewStats(input: {businessId: $id, businessType: $businessType}) { analysis { votedKeyword {details {displayName}}}}}",
                "variables": {
                    "businessType": "restaurant",
                    "id": f"{place_id}"
                }
            }
            response = requests.post(self.review_url, headers=self.review_headers, data=json.dumps(request_data), timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while making POST request: {e}")
            return None

        try: 
            response_data = response.json()
        except requests.exceptions.JSONDecodeError as e:
            print(f'Invalid response: {e}')
            return None
        
        try: 
            likes = response_data['data']['visitorReviewStats']['analysis']['votedKeyword']['details']
            likes = [obj['displayName'] for obj in likes]
        except KeyError:
            print(f'Unexpected response structure')
            return None

        return likes
    
    def scrape_reviews(self, place_id):
        try: 
            data = {
                "operationName": "getVisitorReviewPhotosInVisitorReviewTab",
                "query": "query getVisitorReviewPhotosInVisitorReviewTab($businessId: String!, $businessType: String, $page: Int, $display: Int) {visitorReviews(input: {businessId: $businessId, businessType: $businessType, page: $page, display: $display, isPhotoUsed: true}) {items {body media { type thumbnail }visited votedKeywords {displayName }} }}",
                "variables": {
                    "businessId": f"{place_id}",
                    "businessType": "restaurant",
                    "page": 1,
                    "display": 20
                }
            }
            response = requests.post(self.review_url, headers=self.review_headers, data=json.dumps(data), timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error occurred while making POST request: {e}")
            return None

        try:
            response_data = response.json()
        except requests.exceptions.JSONDecodeError as e:
            print(f'Invalid response: {e}')
            return None
        
        try:
            reviews = response_data['data']['visitorReviews']['items']
        except KeyError:
            print(f'Unexpected response structure')
            return None

        review_conversion_rule = {
            'content': {
                'lookup': ['body'],
            }, 
            'created_at': {
                'lookup': ['visited'],
                'post_apply': [to_date, timezone.make_aware]
            }, 
            'likes': {
                'lookup': ['votedKeywords'],
                'post_apply': [lambda lst: [obj['displayName'] for obj in lst]]
            }
        }

        media_to_image_urls_rule = {
            'images': {
                'lookup': ['media'],
                'post_apply': [get_at_most_three_photo_urls]
            },
        }

        images_url_to_images_rule = {
            'image_1': {
                'lookup': ['images', 0], 
                'post_apply': [download_img, ]
            }, 
            'image_2': {
                'lookup': ['images', 1], 
                'post_apply': [download_img, ]
            }, 
            'image_3': {
                'lookup': ['images', 2], 
                'post_apply': [download_img, ]
            }, 
        }

        converted_reviews = NestedDictConverter.convert_list_by_rules(reviews, review_conversion_rule)
        image_urls = NestedDictConverter.convert_list_by_rules(reviews, media_to_image_urls_rule)
        images = NestedDictConverter.convert_list_by_rules(image_urls, images_url_to_images_rule)

        for i in range(len(converted_reviews)):
            converted_reviews[i].update(images[i])

        return converted_reviews

    def scrape_reviews_and_likes(self, place_id):
        # get list of likes of this place
        print(f'called: scrape_reviews_and_likes({place_id})')

        likes = self.scrape_likes(place_id)
        if likes is None:
            likes = []

        # get list of reviews of this place
        reviews = self.scrape_reviews(place_id)
        if reviews is None:
            reviews = []
        
        return None if not (likes or reviews) else {
            'likes': likes, 
            'reviews': reviews,
        }