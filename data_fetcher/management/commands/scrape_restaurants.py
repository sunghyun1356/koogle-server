import decimal
import time

from django.core.management.base import BaseCommand
from django.db.models import Q

from data_fetcher.source_scrapers import TasteOfSeoulScraper
from data_fetcher.naver_scrapers import NaverScraper
from data_fetcher.utils import NestedDictConverter

from Restaurants.models import Food, Menu, OpenHours, Restaurant, Restaurant_Food

class Command(BaseCommand):
    help = 'Scrape verified restaurants from predefined sources, add Naver Place information and save it to the database'

    @staticmethod
    def get_map_link(place_id):
        if not place_id:
            return ''
        return NaverScraper.detail_url % place_id
    
    # TODO: image_url의 이미지를 다운받고 경로를 menu['image']에 저장
    @staticmethod
    def get_menu_images_from_img_url(menus):
        print(f'Menus: {menus}')

        if not menus: 
            return None

        for menu in menus:
            if 'image_url' in menu:
                del menu['image_url']
            menu['image'] = None

        return menus
    
    # TODO: image_url의 이미지를 다운받고 경로를 저장
    def get_image_from_url(img_url):
        return None
    
    @staticmethod
    def rename_description(menus):
        if not menus: 
            return None

        for menu in menus:
            if 'description' in menu:
                menu['content'] = menu['description']
                del menu['description']
        
        return menus
    
    @staticmethod
    def price_to_decimal(menus):
        if not menus: 
            return None

        for menu in menus:
            if 'price' in menu:
                try: 
                    menu['price'] = decimal.Decimal(menu['price'])
                except (decimal.InvalidOperation, decimal.InvalidContext):
                    print(f'Decimal error on {menu["price"]} of menu {menu}')
                    menu['price'] = None
        
        return menus

    restaurant_model_rules = {
        'name': {
            'lookup': ['name'],
        }, 
        'address': {
            'lookup': ['naver', 'address'],
        },
        'image': {
            # TODO: URL의 이미지 다운로드하고 로컬에 저장, DB에 경로 주기
            # TODO: 소스 이미지 URL을 우선시, 네이버 이미지 URL로 가도록 만들기
            'lookup': ['image_url'],
            'post_apply': [get_image_from_url]
        }, 
        'phone': {
            'lookup': ['phone'],
        },
        'map_link': {
            'lookup': ['naver', 'place_id'], 
            'post_apply': [get_map_link]
        },
        'latitude': {
            'lookup': ['naver', 'latitude'], 
            'post_apply': [float]
        },
        'longitude': {
            'lookup': ['naver', 'longitude'], 
            'post_apply': [float]
        },
        'reservation_link': {
            'lookup': ['naver', 'reservation_link'], 
        },
    }

    restaurant_related_rules = {
        'name': {
            'lookup': ['name'],
        }, 
        'menu_detail': {
            'lookup': ['naver', 'menu'],
            'post_apply': [get_menu_images_from_img_url, rename_description, price_to_decimal]
        },
        'open_hours': {
            'lookup': ['naver', 'open_hours'],
        }
    }

    restaurant_food_rules = {
        'name': {
            'lookup': ['name'],
        }, 
        'description': {
            'lookup': ['description']
        },
        'keywords': {
            'lookup': ['naver', 'keywords']
        }
    }

    def handle(self, *args, **options):
        sources = [
            TasteOfSeoulScraper, 
        ]

        restaurants = []
        for src in sources:
            restaurants.extend(src().scrape())

        naver_scraper = NaverScraper()
        for place in restaurants:
            if place.get('phone', None):
                query = place['phone']

                # TODO: handle exceptions by requests.get()
                search_res = naver_scraper.search_place(query)
                if search_res:
                    place['naver'] = search_res
                    detail_res = naver_scraper.scrape_details(search_res['place_id'])
                    if detail_res:
                        place['naver'] = {**search_res, **detail_res}
            
            elif place.get('name', None):
                query = place['name']

                # TODO: handle exceptions by requests.get()
                search_res = naver_scraper.search_place(query)
                if search_res:
                    place['naver'] = search_res
                    detail_res = naver_scraper.scrape_details(search_res['place_id'])
                    if detail_res:
                        place['naver'] = {**search_res, **detail_res}
            
            time.sleep(5)
        
        print(f'scrape restaurants got {len(restaurants)} restaurants:')
        for place in restaurants:
            for (k, v) in place.items():
                print(f'{k:<16}{str(v)}')
            print('\n')
        print('\n')

        converted_restaurants = NestedDictConverter.convert_list_by_rules(restaurants, self.restaurant_model_rules)
        for rst in converted_restaurants:
            rst_obj, _ = Restaurant.objects.update_or_create(name=rst['name'], defaults=rst)

        restaurants_related_info = NestedDictConverter.convert_list_by_rules(restaurants, self.restaurant_related_rules)
        for rst in restaurants_related_info:
            rst_obj = Restaurant.objects.get(name=rst['name'])

            open_hours = rst['open_hours']
            OpenHours.update_restaurant_open_hours(rst_obj, open_hours)

            menus = rst['menu_detail']
            Menu.update_restaurant_menus(rst_obj, menus)

        restaurants_food_hints = NestedDictConverter.convert_list_by_rules(restaurants, self.restaurant_food_rules)
        for rst in restaurants_food_hints:
            related_foods = Food.objects.none()

            # 1. food name exact match in keywords
            if rst['keywords']:
                rst['keywords'] = [word.replace(' ', '').replace('_', '') for word in rst['keywords']]
                related_foods = related_foods.union(Food.objects.filter(name__in=rst['keywords']))

            # 2. food name partial match in description
            if rst['description']:
                description = rst['description'].replace(' ', '')
                food_names = Food.objects.values_list('name', flat=True)

                query_conditions = Q()
                for name in food_names:
                    if name in description:
                        query_conditions |= Q(name=name)
                        print(f'{name} in description')
                
                if query_conditions != Q():
                    related_foods = related_foods.union(Food.objects.filter(query_conditions)) 

            if len(related_foods) == 0:
                Food.objects.get_or_create(name='기타')
                related_foods = Food.objects.filter(name='기타')
            restaurant_obj = Restaurant.objects.get(name=rst['name'])

            Restaurant_Food.update_restaurant_foods(restaurant_obj, related_foods)

        self.stdout.write(self.style.SUCCESS('Scraping completed'))