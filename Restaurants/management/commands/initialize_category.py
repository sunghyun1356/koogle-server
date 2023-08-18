from django.core.management.base import BaseCommand
from Restaurants.models import Category, Food


class Command(BaseCommand):
    help = 'Initialize categories, foods'
    categories = {
        '한식': [
            '떡볶이', 
            '냉면', 
            '불고기', 
            '떡갈비', 
            '육회', 
            '백반', 
            '족발', 
            '보쌈', 
            '찌개', 
            '찜', 
            '닭볶음탕', 
            '삼겹살', 
            '소고기', 
            '곱창', 
            '치킨', 
            '돈까스',
        ], 
        '양식': [
            '스파게티', 
            '햄버거', 
            '피자', 
            '샐러드', 
            '스테이크',
        ],
        '일식': [
            '돈카츠', 
            '라멘', 
            '스시', 
            '카레',
        ],
        '중식': [
            '짜장면', 
            '딤섬', 
            '마라탕', 
            '마라샹궈', 
            '양꼬치',
        ],
        '카페': [
            '케이크',
            '마카롱',
            '아이스크림',
            '도넛',
            '테라스',
        ],
        '그 외': [
            '베트남', 
            '태국', 
            '멕시칸', 
            '인도', 
            '해산물',
            '파인다이닝',
            '기타',
        ]
    }

    def handle(self, *args, **options):
        
        for category, foods in self.categories.items():
            category_obj, _ = Category.objects.get_or_create(name=category)
            
            for food in foods:
                Food.objects.get_or_create(category=category_obj, name=food)

        self.stdout.write(self.style.SUCCESS('Categories initialized'))

        return 0