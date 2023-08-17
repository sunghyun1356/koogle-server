import decimal
import time

from django.core.management.base import BaseCommand
from django.db.models import Q

from data_fetcher.source_scrapers import TasteOfSeoulScraper
from data_fetcher.naver_scrapers import NaverScraper
from data_fetcher.utils import NestedDictConverter, download_img

from Reviews.models import Likes_Restaurant, Review, Review_Likes
from Restaurants.models import Food, Menu, OpenHours, Restaurant, Restaurant_Food

class Command(BaseCommand):
    help = 'Scrape verified restaurants from predefined sources, add Naver Place information and save it to the database'

    @staticmethod
    def get_map_link(place_id):
        if not place_id:
            return ''
        return NaverScraper.detail_url % place_id
    
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
    
    @staticmethod
    def download_menu_images(menus):
        if not menus: 
            return None

        for menu in menus:
            url = menu.get('image_url', None)
            image = download_img(url)
            if image: 
                menu['image'] = image
            del menu['image_url']

        return menus

    restaurant_model_rules = {
        'name': {
            'lookup': ['name'],
        }, 
        'address': {
            'lookup': ['naver', 'address'],
        },
        'image': {
            'lookup': ['image_url'],
            'post_apply': [download_img]
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
        'menu': {
            'lookup': ['naver', 'menu'],
            'post_apply': [download_menu_images, rename_description, price_to_decimal]
        },
        'open_hours': {
            'lookup': ['naver', 'open_hours'],
        }
    }

    restaurant_food_rules = {
        'description': {
            'lookup': ['description']
        },
        'keywords': {
            'lookup': ['naver', 'keywords']
        }
    }

    def exclude_duplicate_restaurants(self, restaurants):
        unique_restaurants = []
        seen_names = set()
        for restaurant in restaurants:
            if restaurant["name"] not in seen_names:
                unique_restaurants.append(restaurant)
                seen_names.add(restaurant["name"])
        
        return unique_restaurants
    
    def scrape_restaurants(self, restaurants):
        restaurants = self.exclude_duplicate_restaurants(restaurants)
        self.stdout.write(self.style.NOTICE(f'Got {len(restaurants)} restaurants from source'))

        naver_scraper = NaverScraper()
        for restaurant in restaurants:
            queries = []
            if restaurant.get('phone', False):
                queries.append(restaurant['phone'])
            if restaurant.get('name', False):
                queries.append(restaurant['name'])

            for query in queries:
                # get general info on restaurant -> restaurant['naver']
                search_res = naver_scraper.search_place(query)
                if search_res is None:
                    time.sleep(5)
                    continue
                
                restaurant['naver'] = search_res
                place_id = search_res['place_id']

                # get detailed info on restaurant -> restaurant['naver']
                details = naver_scraper.scrape_details(place_id)
                if details is None: 
                    time.sleep(5)
                    continue

                restaurant['naver'].update(details)

                # get reviews, likes info on restaurant -> restaurant['naver']
                reviews_likes = naver_scraper.scrape_reviews_and_likes(place_id)
                if reviews_likes is None:
                    time.sleep(5)
                    continue
                    
                restaurant['naver'].update(reviews_likes)
                
                # wait 5 seconds - shorter time makes naver mad
                time.sleep(5)
        
        restaurant_instances = []

        self.stdout.write(self.style.NOTICE(f'Add restaurants to database'))
        restaurant_dicts = NestedDictConverter.convert_list_by_rules(restaurants, self.restaurant_model_rules)
        for rst in restaurant_dicts:
            print(f'{rst}')

            restaurant, _ = Restaurant.objects.update_or_create(name=rst['name'], defaults=rst)

            restaurant_instances.append(restaurant)

        self.stdout.write(self.style.NOTICE(f'Add open hours, menus of restaurants to database'))

        details_restaurant = NestedDictConverter.convert_list_by_rules(restaurants, self.restaurant_related_rules)
        for i in range(len(restaurant_instances)):
            open_hours = details_restaurant[i].get('open_hours', [])
            OpenHours.update_restaurant_open_hours(restaurant_instances[i], open_hours)

            menus = details_restaurant[i].get('menu', [])
            Menu.update_restaurant_menus(restaurant_instances[i], menus)
        
        self.stdout.write(self.style.NOTICE(f'Relate Food with restaurant'))
        food_hints_restaurant = NestedDictConverter.convert_list_by_rules(restaurants, self.restaurant_food_rules)
        for i in range(len(restaurant_instances)):
            related_foods = Food.objects.none()

            # 1. keyword에서 Food가 발견되면 연결
            keywords = food_hints_restaurant[i].get('keywords', None)
            if keywords:
                keywords = [word.replace(' ', '').replace('_', '') for word in keywords]
                related_foods = related_foods.union(Food.objects.filter(name__in=keywords))
            
            # 2. description에서 Food가 발견되면 연결
            description = food_hints_restaurant[i].get('description', None)
            if description:
                description = description.replace(' ', '')
                food_names = Food.objects.values_list('name', flat=True)

                query_conditions = Q()
                for name in food_names:
                    if name in description:
                        query_conditions |= Q(name=name)
                
                if query_conditions != Q():
                    related_foods = related_foods.union(Food.objects.filter(query_conditions))
            
            Restaurant_Food.update_restaurant_foods(restaurant_instances[i], related_foods)

        self.stdout.write(self.style.NOTICE(f'Add likes, reviews on restaurant'))
        for i in range(len(restaurant_instances)):
            rst_obj = restaurant_instances[i]

            likes = restaurants[i]['naver']['likes']
            reviews = restaurants[i]['naver']['reviews']

            reviews_without_likes = [{k: v for k, v in rvw.items() if k != 'likes'} for rvw in reviews]
            review_with_likes_only = [{k: v for k, v in rvw.items() if k == 'likes'} for rvw in reviews]

            Likes_Restaurant.update_restaurant_likes(rst_obj, likes)
            review_instances = Review.update_restaurant_reviews(rst_obj, reviews_without_likes)

            for j in range(len(review_instances)):
                Review_Likes.update_review_likes(review_instances[j], review_with_likes_only[j]['likes'])

    def handle(self, *args, **options):
        sources = [
            TasteOfSeoulScraper, 
        ]

        all_restaurants = []
        for src in sources:
            all_restaurants.extend(src().scrape())

        # Scrape three restaurants at a time - may have memory issue due to all image files being loaded at once
        for i in range(0, len(all_restaurants), 3):
            restaurants = all_restaurants[i:i+3]
            self.scrape_restaurants(restaurants)

        self.stdout.write(self.style.SUCCESS('Scraping completed'))

        return 0