import requests
from bs4 import BeautifulSoup
import json

from .utils import to_time, to_day_of_week_eng, NestedDictConverter

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
            print(f'Unable to get business hours of {str(place_obj)[:20]}...\n')
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
        
        response = requests.get(url)
        response.raise_for_status()

        page = BeautifulSoup(response.content, 'html.parser')
        script_tags = page.find('body').find_all('script')
        if (len(script_tags) < 3):
            print('less than three script tags\n')
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
            if not place_info:
                continue

            for key, val in place_info.items():
                res[key] = val

        return res

    def search_place(self, query):
        print(f'called: search_place({query})')

        url = self.list_url
        params = self.list_params
        params['query'] = query

        response = requests.get(url, params, timeout=5)
        response.raise_for_status()

        try: 
            place = response.json()['result']['site']['list'][0]
        except (NameError, TypeError) as e:
            print(f'No search result: query was {query}\n')
            return None
        
        res = {}

        for (naver_key, key) in self.list_result_conversion.items():
            res[key] = place[naver_key]
            if naver_key == 'id': 
                res[key] = res[key][1:] # drop first letter
            
        return res