import decimal
import time

from django.core.management.base import BaseCommand
from Restaurants.models import Menu, OpenHours, Restaurant

from data_fetcher.source_scrapers import TasteOfSeoulScraper
from data_fetcher.naver_scrapers import NaverScraper
from data_fetcher.utils import NestedDictConverter

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

    def handle(self, *args, **options):
        sources = [
            TasteOfSeoulScraper, 
        ]

        restaurants = []
        for src in sources:
            restaurants.extend(src().scrape())

        # # FOR TEST
        restaurants = restaurants[6:8]

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
            
        for place in restaurants:
            for (k, v) in place.items():
                print(f'{k:<16}{str(v)}')
            print()

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

            

        self.stdout.write(self.style.SUCCESS('Scraping completed'))