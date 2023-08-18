from django.shortcuts import render
import datetime
import geopy.distance
from collections import Counter
import os
from dotenv import load_dotenv
from django.db.models import Count,F
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from geopy.distance import great_circle
from django.contrib.gis.measure import Distance

from Papago_API import translate_and_extract

from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
translated_restaurants_name = {
    "로칸다몽로": "Rocanda Mongro",
    "르끄띠엘푸": "Le Petit Pou",
    "미로식당": "Miro Restaurant",
    "미카야": "Mikaya",
    "빠넬로": "Banello",
    "스파카나폴리": "Spakana Poly",
    "옥동식": "Okdong Sik",
    "우도카덴": "Udo Kaden",
    "윤서울": "Yoon Seoul",
    "이키류": "Ikiryu",
    "진진가연": "Jinjin Gayeon",
    "팬앤콜": "Fan and Call",
    "하카다분코": "Hakada Bunko",
    "구스토타코": "Gusto Tako",
    "레이크커피바": "Lake Coffee Bar",
    "맛이차이나": "Mati China",
    "몰토베네": "Moltobene",
    "백세식당": "Baekse Siktang",
    "부탄츄": "Butan Chu",
    "밀로커피로스터스": "Milo Coffee Roasters",
    "산띠": "Santi",
    "블로트커피": "Blot Coffee",
    "빈브라더스": "Bean Brothers",
    "산울림 1992": "San Ulrim 1992",
    "쉐시몽": "C'est Si Bon",
    "아이덴티티커리랩": "Identity Curry Lab",
    "앤트러사이트": "Entro Site",
    "오리지널시카고피자": "Original Chicago Pizza",
    "온블랙94": "On Black 94",
    "웃사브": "Wootsab",
    "천이오겹살": "Cheon I Ogyeopsal",
    "츄리츄리": "Churi Churi",
    "커피상점이심": "Coffee Sangjeom I Sim",
    "쿠시무라": "Kushimura",
    "쿠시카츠쿠시엔": "Kushikatsu Kushien",
    "퀜치커프": "Quenchi Kup",
    "피오니": "Peony",
    "그로니": "Groni",
    "안동한우마을": "Andong Hanu Maeul",
    "이츠모라멘": "Itsumo Ramen",
    "어썸도넛서울": "Awesome Donut Seoul",
    "자이온보트": "Zai On Boat",
    "카밀로라자네리아": "Camillo Razzaneria",
    "츄로101": "Churro 101",
    "쿠바왕": "Cuba King",
    "띵크프룻": "Thinq Fruit",
    "하카타나카": "Hakata Nakka",
    "비스트로세노": "Bistro Seno",
    "청기와타운(홍대점)": "Cheonggiwa Town (Hongdae Branch)",
    "코이누르(홍대점)": "Koinuru (Hongdae Branch)",
    "가츠시": "Gatsushi",
    "가미우동": "Gami Udon",
    "경주식당": "Gyeongju Sikdang",
    "개화기요정": "Gaehwa Kiyoteong",
    "강수곱창": "Gangsu Gobchang",
    "골드피쉬딤섬익스트레스": "Goldfish Dim Sum Express",
    "고집": "Gojib",
    "공중도시": "Gongjung Dosi",
    "광동포차": "Gwangdong Pocha",
    "괴르츠": "Georcheu",
    "그랭블레": "Grable",
    "그문화다방": "Geumunhwa Dabang",
    "기요한": "Giyohan",
    "길모퉁이칠리차차": "Gilmotungi Chili Chacha",
    "김씨네심야식당": "Kim's Late-Night Restaurant",
    "남경장": "Namgyeong Jang",
    "다락투": "Darak Tu",
    "누바닥터마르": "Nuba Doctor Mar",
    "달의계단": "Dari Gye Dan",
    "담소": "Damsa",
    "달술집": "Dalsuljib",
    "더캐스크": "The Cask",
    "당고집": "Danggo Jib",
    "더담": "The Dam",
    "데코아발림": "Decoa Vallim",
    "더페이머스램": "The Famous Ram",
    "도마": "Doma",
    "동꾼": "Dongkkun",
    "두레차": "Dure Cha",
    "동강해물찜": "Donggang Haemuljjim",
    "두리반": "Duriban",
    "라오": "Rao",
    "디스틸": "Distil",
    "럭키스트라이크": "Lucky Strike",
    "로로11": "Loro 11",
    "레드플랜트": "Red Plant",
    "림가기": "Rim Gagi",
    "루시드서울": "Lucid Seoul",
    "마녀커리크림치킨(상수점)": "Witch Curry Cream Chicken (Sangsuj",
    "마차회집": "Macha Hoegwe",
    "마츠에라멘": "Matsueramen",
    "막걸리싸롱": "Makgeolli Ssalong",
    "멘야산다이메": "Menya Sandaime",
    "멘야하나비합정점": "Menya Hanabi Hapjeongjeom",
    "멜로우": "Mellow",
    "명성관": "Myeongseonggwan",
    "명품잔치국수": "Myeongpum Janchi Guksu",
    "모리츠플라츠오오엠": "Moritzplatz Oem",
    "몽카페그레고리": "Mon Cafe Gregory",
    "무대륙": "Mudaeruk",
    "무명집": "Mummyeongjib",
    "무판": "Mupan",
    "문숙이미나리식당": "Munsuk's Minari Sikdang",
    "미식가주택": "Miseukgahutak",
    "뭄알로이": "Meom Alloi",
    "미담진족": "Midam Jinjok",
    "백년토종삼계탕": "Baeknyeon Tojong Samgyetang",
    "미티": "Miti",
    "바다포차실리": "Badapocha Silli",
    "버들고이야기(상수점)": "Beodeul Goiyagi (Sangsuj",
    "백소정(홍대합정점)": "Baek Sojeong (Hongdae-Hapjeong Branch)",
    "버거4.5": "Burger 4.5",
    "별밤": "Byeolbam",
    "베이스캠프": "Base Camp",
    "별버거": "Byeol Burger",
    "브렛피자": "Bret Pizza",
    "브루브로스커피": "Brew Bros Coffee",
    "브뤼서리서교": "Bruxelles Serry Seogyo",
    "비닐": "Vinyl",
    "비사벌전주콩나물국밥(합정점)": "Bissabel Jeonju Kongnamul Gukbap (Hapjeong Branch)",
    "비스트로사랑방": "Bistro Sarangbang",
    "빌리커피로스터스": "Billy Coffee Roasters",
    "살로또상수": "Salotto Sangsu",
    "삼거리포차": "Samgeori Pocha",
    "살사리까": "Salsarikka",
    "샴락앤롤아이리쉬펍": "Shamrock & Roll Irish Pub",
    "서교로터리": "Seogyo Rotary",
    "서강껍데기소금구이소막창": "Seogang Kkeopdegi Sogeumgui Somakchang",
    "설참치(2호점)": "Seol Chamchi (2nd Branch)",
    "성화라멘": "Seonghwa Ramen",
    "세상의끝의라멘": "Sesangui Ggeutui Ramen",
    "손탁커피": "Sontak Coffee",
    "쇼콜라윰": "Chocola Yum",
    "슈아브": "Suave",
    "송탄영빈루": "Songtan Youngbinru",
    "스시겐": "Sushi Gen",
    "스노브": "Snob",
    "슬런치팩토리": "Slunch Factory",
    "시연": "Siyeon",
    "시간의공기": "Siganeui Gonggi",
    "신주양꼬치(홍대본점)": "Shinju Yangkkochi (Hongdae Branch)",
    "신미경홍대닭갈비": "Shin Mi Gyeong Hongdae Dakgalbi",
    "신원복집": "Shinwon Bokjip",
    "실루엣커피": "Silhouette Coffee",
    "심양(홍대점)": "Simyang (Hongdae Branch)",
    "아날로그가든": "Analog Garden",
    "아오이토리": "Aoi Tori",
    "아지트": "Azit",
    "아트스페이스우월": "Art Space Woo Wo",
    "알디프티바": "Aldi PT Bar",
    "어메이징타일랜드": "Amazing Thailand",
    "언더크레마": "Under Cream",
    "에고": "Ego",
    "에도마에텐동하마다": "Edomae Tendon Hamada",
    "연과점 하루": "Yeongwa Jeom Haru",
    "영빈": "Youngbin",
    "예티": "Yeti",
    "옛맛서울불고기": "Yetmat Seoul Bulgogi",
    "오너쉐프": "Owner Chef",
    "오비야": "Obiya",
    "오스테리아오라": "Osteria Ora",
    "오스틴": "Austin",
    "오자와": "Ozawa",
    "옹다래찜닭": "Ongda Rae Jjim Dak",
    "옹달샘": "Ongdal Saem",
    "우디네": "Woodine",
    "요츠야": "Yotsuya",
    "우마담": "Umadam",
    "웨스턴철판볶음밥": "Western Cheonpan Bokkeumbap",
    "유니크스위트": "Unique Sweet",
    "윤시밀방": "Yoon Simil Bang",
    "유메": "Yume",
    "이리카페": "Iri Cafe",
    "이태원겐지스": "Itaewon Genesis",
    "이빠네마그릴(홍대점)": "Ippane Magril (Hongdae Branch)",
    "제비다방": "Jebi Dabang",
    "제주정원": "Jeju Jeongwon",
    "제임스시카고피자": "James Chicago Pizza",
    "조개이야기": "Jogaegi Yagi",
    "주행": "Juhang",
    "줄라이13": "Julla I 13",
    "지로우라멘": "Jirou Ramen",
    "진저피그": "Jinjer Pig",
    "진향": "Jinhyang",
    "철길왕갈비살": "Cheolgil Wang Galbisal",
    "초마": "Choma",
    "초이다이닝": "Choi Dining",
    "춘자대구탕": "Choonja Daegu Tang",
    "츠케루": "Tsukeru",
    "카레시": "Karéshi",
    "카와카츠": "Kawakatsu",
    "카시와": "Kashiwa",
    "카페모노블록": "Cafe Monoblock",
    "카페더블루스": "Cafe The Blues",
    "카페새록": "Cafe Saerok",
    "커피101": "Coffee 101",
    "커피랩": "Coffee Lab",
    "칼디커피서덕식": "Kaldi Coffee Seodeok Sik",
    "코노미": "Conomi",
    "커피발전소": "Coffee Baljeonso",
    "코다차야(홍대점)": "Kodachaya (Hongdae Branch)",
    "쿡앤북": "Cook and Book",
    "쿠이신보": "Kuishinbo",
    "크림LP바": "Cream LP Bar",
    "클럽에반스": "Club Evans",
    "타이스퀘어": "Thai's Square",
    "탐라식당": "Tamra Sikdang",
    "테일러커피(서교점)": "Taylor Coffee (Seogyo Branch)",
    "텟판타마고": "Tetpan Tamago",
    "토라슌": "Torashun",
    "톤앤매너": "Tone & Manner",
    "팩토리": "Factory",
    "펍원": "Pub One",
    "퍼셉션": "Perception",
    "풀잎향기": "Pulip Hyanggi",
    "플레이트946": "Plate 946",
    "프리바다727": "Freebada 727",
    "하꼬": "Hako",
    "호호미욜": "Hohomi Yol",
    "한석화": "Han Seokhwa",
    "혼카츠": "Honkatsu",
    "홍대삭": "Hongdae Salk",
    "홈프롬귀": "Homprom Gwi",
    "홍대조폭떡볶이": "Hongdae Jopok Tteokbokki",
    "홍어한마리": "Hongeo Hanmari",
    "홍쉐프홍익숯불갈비소금구이": "Hong Chef Hong Ik Charcoal Grilled Salted Galbi",
    "훌리오": "Hulio",
    "흥부네부대찌개": "Heungbu's Budae Jjigae",
    "히메시야": "Himeshia"
}

load_dotenv()
client_id = "A1myJv4j7i0k0jVxswja" # 개발자센터에서 발급받은 Client ID 값
client_secret = "_7xoqsu5d0" # 개발자센터에서 발급받은 Client Secret 값
from .models import *
from Reviews.models import *
# Create your views here.
from .serializers import *

# 이름, 전화번호, 주소, 오픈, 클로즈 시간, 예약 유무, 가게 사진 필요
# 현재 내위치가 가게로 부터 몇미터 떨어져 있는지 -> 계산 필요
# 몇 쿠글로 예상이 되는지 -> 계산 필요 ( 유저와 네이버를 통해서 각각 )
# 

def translate_data(data):
    translated_data = {}

    for key, value in data.items():
        if isinstance(value, str):  # 문자열인 경우에만 번역 수행
            translated_text = translate_and_extract(value)
            translated_data[key] = translated_text if translated_text is not None else value  # 수정된 부분
        elif isinstance(value, dict):  # 중첩된 딕셔너리인 경우 재귀적으로 번역 수행
            translated_data[key] = translate_data(value)
        else:
            translated_data[key] = value  # 문자열이 아닌 경우 그대로 유지

    return translated_data

@api_view(['GET'])
def get_restaurants_by_food(request, food_id):
    selected_items = request.query_params.getlist('food_id', [])
    sort_by = request.query_params.get('sort_by')
    if not selected_items:
        return Response({"error": "No selected items provided"}, status=400)

    user_latitude = request.data.get('37.5508')  # 사용자 위치의 위도
    user_longitude = request.data.get('126.9255')  # 사용자 위치의 경도

    restaurants = Restaurant.objects.filter(
        restaurant_food_restaurant__food__id__in=selected_items
    )
    if sort_by == 'distance':
        # 거리를 계산하여 응답 데이터에 추가
        serialized_data = []
        for restaurant in restaurants:
            restaurant_latitude = restaurant.latitude
            restaurant_longitude = restaurant.longitude
            distance = great_circle(
                (restaurant_latitude, restaurant_longitude),
                (user_latitude, user_longitude)
            ).meters
            serialized_data.append({
                "restaurant_info": RestaurantBaseSerializer(restaurant).data,
                "distance": distance  
            })
        for i in serialized_data:
            i["name"] = translate_and_extract(i["name"])
                
    #평점순 정렬
    elif sort_by == 'rating':
        restaurants = restaurants.order_by('-koogle_ranking')
        serialized_data = RestaurantBaseSerializer(restaurants, many=True).data
    return Response({"restaurants":serialized_data })



class MainpageAPIView(APIView):
    qeuryset = Food.objects.all()
    serializers = CategoryFoodSerializer
    permission_classes = [AllowAny]
    def get(self, request):
        data ={}
        categories = Category.objects.all()
        for category in categories:
            food_list = Food.objects.filter(category=category)
            food_data = {}
            for food_listing in food_list:
                category.name = translate_and_extract(category.name)
                data[category.name] =food_listing.id
            data[category.name] = food_data
        return Response({"data" : data})

class FoodSelectedRestaurantsAPIView(APIView):
        queryset = Restaurant.objects.all()
        serializers = FoodSelectedRestaurantSerializer
        permission_classes = [AllowAny]
        def get(self, request, food_ids):
            selected_items = request.query_params.getlist('food_ids', [])
            food_ids = [int(food_id) for food_id in selected_items if food_id.isdigit()]
            restaurants_list = []
            for food_ids_list in food_ids:
                selected_restaurants = Restaurant.objects.filter(food__id=food_ids_list)
                for rest in selected_restaurants:
                    restaurants_list.append(rest)
            restaurants_list = list(set(restaurants_list))
            # 레스토랑 이름, 주소, 번호, 거리, 쿠글
            data = {}
            for each_restaurants in restaurants_list:
                each_restaurants_name = translate_and_extract()
                restaurant_data ={}
                if  each_restaurants_name in translated_restaurants_name:
                    restaurant_base.name = translated_restaurants_name[restaurant_name]
                else:
                    restaurant_base.name = translate_and_extract(restaurant_base.name)

            
            





#검색창
@api_view(['GET'])
def search_restaurants(request):
    search_query = request.GET.get('q')  # 검색
    
    if search_query:
        matching_restaurants = Restaurant.objects.filter(name__icontains=search_query)
        serialized_data = RestaurantBaseSerializer(matching_restaurants, many=True).data
        return Response(serialized_data)
    else:
        return Response([])
    



def koogle_cal(a,b):
    if 0<= (a / b)/5 < 1.5:
        c =1
    elif 1.5 <= (a / b)/5 < 3:
        c =2
    elif 3 <= (a/b)/5:
        c=3
    return c 



class RestaurantsBaseAPIView(APIView):
    queryset = Restaurant.objects.all()
    serializers_class = RestaurantBaseSerializer
    permission_classes = [AllowAny]
    
    def get(self, request, restaurant_name ):
        data = dict()

        try:
            restaurant_base = get_object_or_404(Restaurant, name=restaurant_name)
        except Restaurant.DoesNotExist:
            raise NotFound("Restaurant not found")
        
        try:
            naver_users = User.objects.filter(is_staff=True)
        except User.DoesNotExist:
            raise NotFound("User not found")
        try:
            user_users = User.objects.filter(is_staff=False)
        except User.DoesNotExist:
            raise NotFound("User not found")
        # 오픈시간 클로즈시간 가져오기

        # 번역 완료
        open_close_data ={}
        open_close = OpenHours.objects.all()
        for open_hours in open_close:
            restaurant_name = open_hours.restaurant.name
            day =open_hours.day
            open_time = open_hours.open_time.strftime('%H:%M %p')
            close_time = open_hours.close_time.strftime('%H:%M %p')
            day =translate_and_extract(day)
            open_close_data[day] ={
                'open_time' : open_time,
                'close_time' : close_time,
            }

        # for문으로 돌리면서 리스트에 담아주고 또 이걸 분류를 해주어야 한다
        restaurant_latitude = restaurant_base.latitude
        restaurant_longtitude = restaurant_base.longitude
            
        # 추후 api받아와서 설정 할 것
        current_latitude = 37.5508
        current_longtitude =126.9255
            #계산
        distance = geopy.distance.distance((current_latitude,current_longtitude), (restaurant_latitude,restaurant_longtitude)).m
            # 이미지 없을시 설정
        if restaurant_base.image == None:
            restaurant_base.image = "None"
        
        # 완료
        restaurant_menu = Menu.objects.filter(restaurant=restaurant_base)
        # __in은 foreign키로 연결되어있을때 역참조를 위한 것
        menu_detail = Menu_Detail.objects.filter(menu__in=restaurant_menu)
        menus=[]
        for detail in menu_detail:
            detail.name = translate_and_extract(detail.name)
            menus.append({
                'name' : detail.name,
                'price': detail.price,
                'image': detail.image,
            })

        
        # 이미지 추가 예정
        #restuarant에서 모든 food를 타고 올라가서 category를 출력 해준다
        # 완료
        base_food = Restaurant_Food.objects.filter(restaurant=restaurant_base)
        categories =[]
        for food_relation in base_food:
            food_relation.food.category.name = translate_and_extract(food_relation.food.category.name)
            categories.append(food_relation.food.category.name)


        naver_review_count_sum = 0
        user_review_count_sum = 0
        naver_review_likes_count_sum =0
        user_review_likes_count_sum =0

        for naver_user in naver_users:

            # naver리뷰수 
            naver_review_count_sum += Review.objects.filter(user=naver_user, restaurant = restaurant_base).count()
            # 레스토랑의 라이크수 합
            naver_review_likes_count_sum  += Review_Likes.objects.filter(review__restaurant=restaurant_base, review__user=naver_user).count()
         
        naver_reviews = Review.objects.filter(user__is_staff=True, restaurant=restaurant_base)
        naver_top_likes = Review_Likes.objects.filter(review__in=naver_reviews).values('likes__likes').annotate(like_count=Count('likes')).order_by('-like_count')[:5]
        
        naver_likes_data ={}
        for likes_info in naver_top_likes:
            likes_name = likes_info['likes__likes']
            likes_count = likes_info['like_count']
            likes_name = translate_and_extract(likes_name)
            naver_likes_data[likes_name] = likes_count

        for user_user in user_users:
            # user리뷰수 
            user_review_count_sum += Review.objects.filter(user=user_user, restaurant = restaurant_base).count()
            # user의 라이크수 합
            user_review_likes_count_sum  += Review_Likes.objects.filter(review__restaurant=restaurant_base, review__user=user_user).count()

        user_reviews = Review.objects.filter(user__is_staff=False, restaurant=restaurant_base)
        user_top_likes = Review_Likes.objects.filter(review__in=user_reviews).values('likes__likes').annotate(like_count=Count('likes')).order_by('-like_count')[:5]
        user_likes_data ={}
        for likes_info in user_top_likes:
            likes_name = likes_info['likes__likes']
            likes_count = likes_info['like_count']
            likes_name = translate_and_extract(likes_name)
            user_likes_data[likes_name] = likes_count
        
        # 레스토랑 정보들 번역 처리
        restaurant_base.address = translate_and_extract(restaurant_base.address),

        
        if restaurant_base.name in translated_restaurants_name:
            restaurant_base.name = translated_restaurants_name[restaurant_name]
        else:
            restaurant_base.name = translate_and_extract(restaurant_base.name) 
            
        data = {
            #이미지 파일 넣으면 postman에서 오류떠서 나중에 넣을게욤
            # 완료
            'name' : restaurant_base.name,

            'phone' : restaurant_base.phone,
            
            'address' : restaurant_base.address,

            'opening_closing_time' : open_close_data,

            'reservation' : restaurant_base.reservation,

            'naver_koogle' : koogle_cal(naver_review_likes_count_sum , naver_review_count_sum),

            'user_koogle' : koogle_cal(user_review_likes_count_sum, user_review_count_sum),
            # 번역필요
            'category':categories,

            'distance' : distance,
            # 번역필요
            'naver_likes_data' : naver_likes_data,
            # 번역필요
            'user_likes_data' : user_likes_data,

            'restaurant_map_url' : restaurant_base.map_link,
            # 번역필요
            'restaurant_menu' : menus,

            'restaurant_image': restaurant_base.image,

        }


        return Response(data)

