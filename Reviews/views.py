from django.shortcuts import render
import datetime
import geopy.distance
import os
from dotenv import load_dotenv
import os
import urllib.parse
import urllib.request


load_dotenv()
client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta

from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListCreateAPIView

from .models import *
from Restaurants.models import *
from .serializers import *
from Users.models import *
load_dotenv()
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


client_id = "A1myJv4j7i0k0jVxswja" # 개발자센터에서 발급받은 Client ID 값
client_secret = "_7xoqsu5d0" # 개발자센터에서 발급받은 Client Secret 값
from Papago_API import translate_and_extract

# Create your views here.
def translate_data(data):
        translated_data = {}

        for key, value in data.items():
            if isinstance(value, str):  # 문자열인 경우에만 번역 수행
                translated_text = translate_and_extract(value)
                translated_data[key] = translated_text if translated_text else value
            elif isinstance(value, dict):  # 중첩된 딕셔너리인 경우 재귀적으로 번역 수행
                translated_data[key] = translate_data(value)
            else:
                translated_data[key] = value  # 문자열이 아닌 경우 그대로 유지

        return translated_data

# review 디테일 페이지 기본 -> 최신순으로 배정

# country별로 뽑아올 때
class ReviewListInfoCountryAPIView(ListCreateAPIView):
    # 객체저장
    queryset = Review.objects.all()
    # serializer시키기
    serializer_class = ReviewUserBaseSerializer
    permission_classes = [AllowAny]
    


    def calculate_time(self, review):
        current = timezone.now()
        gap = current - review.created_at
        days = gap.days
        seconds = gap.seconds
        hours, remain = divmod(seconds, 3600)
        minutes, seconds = divmod(remain, 60)
        return f"{days} days, {hours}hours, {minutes}minutes ago"

    def get_queryset(self):
        country_name = self.request.query_params.get('country_name')
        return country_name

       
    def list(self, request, restaurant_name,country_name, *args, **kwargs):
        data = dict()
        # 레스토랑 베이스 만들기
        try:
            restaurant_base = get_object_or_404(Restaurant, name=restaurant_name)
        except Restaurant.DoesNotExist:
            raise NotFound("Restaurant not found")
        # country 뽑아주고 저장하기
        if country_name is None:
            raise NotFound("Country name not exits")
        # Country 객체 만들어주기
        try:
            user_country = Country.objects.filter(name=country_name)
        except Country.DoesNotExist:
            raise NotFound("Country not exits")
        # 유저 만들어주기
        try:
            country_users = User.objects.filter(is_staff=False, country__in = user_country)
        except User.DoesNotExist:
            raise NotFound("User not found")

        all_countries = Country.objects.values_list('name', flat=True) 
        all_reviews = Review.objects.filter(restaurant=restaurant_base)
        all_likes_list =[]
        for review in all_reviews:
            likes_list = review.review_review_likes.values_list('likes__likes', flat=True)
            all_likes_list.extend(likes_list)
        all_likes_list = list(set(all_likes_list))

        country_reviews = Review.objects.filter(user__in=country_users, restaurant=restaurant_base)
        country_reviews_data = self.get_review_data(country_reviews, restaurant_base)

        restaurants_info = {
            'restaurant_name': restaurant_base.name,
                'address': restaurant_base.address,
                'total_review': Review.objects.filter(restaurant=restaurant_base).count(),
                'avg_star' : Review.objects.filter(restaurant=restaurant_base).aggregate(Avg('star'))['star__avg'],}
        data = {
            'restaurants_info' : restaurants_info,
            'country_reviews': country_reviews_data,
            'country_list' : all_countries,
            'all_likes_list': all_likes_list,
        }

        return Response(data)

    def get_review_data(self, reviews, restaurant_base):
        
        review_data = []
        for review in reviews:
            user_reviews = Review.objects.filter(user=review.user)
            total_review_count = user_reviews.count()
            total_image_count = sum(1 for r in user_reviews if r.image_1 or r.image_2 or r.image_3)
            review_likes = Review_Likes.objects.filter(review=review)
            likes_names = [rl.likes.likes for rl in review_likes]
            data = {
                
                'username': review.user.username,
                'star': review.star,
                'total_review_count': total_review_count,
                'total_image_count': total_image_count,
                'content': review.content,
                'country': review.user.country.name if review.user.country else None,
                'created_at' :  self.calculate_time(review),
                'image_1' : review.image_1,
                'image_2' : review.image_2,
                'image_3' : review.image_3,
                'review_list' :  likes_names
            }
            review_data.append(data)
        
        return review_data
    def post(self, request, *args, **kwargs):
        # request.data로 전송된 데이터를 받아옴
        restaurant_name = kwargs["restaurant_name"]
        
        # restaurant_name을 기반으로 레스토랑 객체 가져옴
        restaurant_id = Restaurant.objects.get(name=restaurant_name)

        # user_id는 현재 요청을 보낸 사용자
        user_id = request.user.id
        # request.data.에 user필드를 추가
        """request.data["user"] = user_id"""
        request.data["restaurant"] = restaurant_id.id
        # serializer로 데이터 검증 및 저장
        # ㅎ해당 요청의 데이터로 초기화된 serializer 객체를 가져온다
        serializer = self.get_serializer(data=request.data)
        # 유효한지 검사를 한다
        serializer.is_valid(raise_exception=True)
        # 검증된 데이터를 기반으로 Review 모델 인스턴스를 생성하고 저장한다.
        review = serializer.save()

        # Likes 선택 여부를 확인하고 Review_Likes, Likes_Restaurant에 자동으로 저장
        likes_data = request.data.get('all_likes_list', [])
        i = 0
        for like_id in likes_data:
            # 각각의 likes_Restaurant에서 likes의 pk를 얻는다.
            if int(like_id) == 1:
                try:
                    # Likes_Restaurant의 객체 중 restaurant가 review.restaurant인 것들을 가져옴
                    like = Likes_Restaurant.objects.filter(restaurant=review.restaurant).order_by('pk')[i]
                    i += 1
                    # Review_Likes와 Likes_Restaurant에 저장
                    Review_Likes.objects.create(review=review, likes=like.likes)
                except (ValueError, Likes_Restaurant.DoesNotExist, IndexError):
                    pass
            else:
                i+=1

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
                    

class ReviewListInfoAPIView(ListCreateAPIView):
    # 객체저장
    queryset = Review.objects.all()
    # serializer시키기
    serializer_class = ReviewUserBaseSerializer
    permission_classes = [AllowAny]
    # 정렬하기 위해서 설정해준다

    def calculate_time(self, review):
        current = timezone.now()
        gap = current - review.created_at
        days = gap.days
        seconds = gap.seconds
        hours, remain = divmod(seconds, 3600)
        minutes, seconds = divmod(remain, 60)
        return f"{days} days, {hours}hours, {minutes}minutes ago"

    def get_queryset(self):
        # 초반 기본 설정은 latest고 get(a,b)일때 query_param에 get으로 a,b를 가져온다는 것이다
        order_by = self.request.query_params.get('order_by', 'latest') 
        if order_by == 'latest':
            return self.queryset.order_by('-created_at')
        elif order_by == 'highest':
            return self.queryset.order_by('-star')
        elif order_by == 'lowest':
            return self.queryset.order_by('star')

    def list(self, request, restaurant_name, *args, **kwargs):
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
        all_countries = Country.objects.values_list('name', flat=True) 
        all_reviews = Review.objects.filter(restaurant=restaurant_base)
        all_likes_list =[]
        for review in all_reviews:
            likes_list = review.review_review_likes.values_list('likes__likes', flat=True)
            all_likes_list.extend(likes_list)
        all_likes_list = list(set(all_likes_list))

        naver_reviews = Review.objects.filter(user__in=naver_users, restaurant=restaurant_base)
        user_reviews = Review.objects.filter(user__in=user_users, restaurant=restaurant_base)
        
        # naver_reviews가 여러개니까 이걸 대체 몇개씩 볼건지를 정한다 -> 4개찍 naver_reviews가 저장되어있다


        # 네이버와 user사용자의 리뷰페이지 번호를 가져오는데 파라미터가 url에 없으면 기본값은 1

        
        #self.함수로 지금 선언된 함수를 사용한다
        naver_reviews_data = self.get_review_data(naver_reviews, restaurant_base)
        # get_page(?_reviews_page로 지금 어느 페이지에 있는지를 가져온다)
        user_reviews_data = self.get_review_data(user_reviews, restaurant_base)
        restaurants_info = {
            'restaurant_name': restaurant_base.name,
                'address': restaurant_base.address,
                'total_review': Review.objects.filter(restaurant=restaurant_base).count(),
                'avg_star' : Review.objects.filter(restaurant=restaurant_base).aggregate(Avg('star'))['star__avg'],}
        data = {
            'restaurants_info' : restaurants_info,
            'naver_reviews': naver_reviews_data,
            'user_reviews': user_reviews_data,
            'country_list'  : all_countries,
            'all_likes_list' : all_likes_list,

        }
        return Response(data)

    def get_review_data(self, reviews, restaurant_base):
        review_data = []
        for review in reviews:
            user_reviews = Review.objects.filter(user=review.user)
            total_review_count = user_reviews.count()
            total_image_count = sum(1 for r in user_reviews if r.image_1 or r.image_2 or r.image_3)
            review_likes = Review_Likes.objects.filter(review=review)
            likes_names = [rl.likes.likes for rl in review_likes]
            data = {
                
                'username': review.user.username,
                'star': review.star,
                'created_at' :  self.calculate_time(review),
                'total_review_count': total_review_count,
                'total_image_count': total_image_count,
                'content': review.content,
                'country': review.user.country.name if review.user.country else None,
                'image_1' : review.image_1,
                'image_2' : review.image_2,
                'image_3' : review.image_3,
                'likes_list': likes_names,
            }

            review_data.append(data)
        
        return review_data
    def post(self, request, *args, **kwargs):
        # request.data로 전송된 데이터를 받아옴
        restaurant_name = kwargs["restaurant_name"]
        
        # restaurant_name을 기반으로 레스토랑 객체 가져옴
        restaurant_id = Restaurant.objects.get(name=restaurant_name)
        user = request.user
        # user_id는 현재 요청을 보낸 사용자
        request.data["user"] = user.id
        # request.data.에 user필드를 추가
        
        request.data["restaurant"] = restaurant_id.id
        # serializer로 데이터 검증 및 저장
        # ㅎ해당 요청의 데이터로 초기화된 serializer 객체를 가져온다
        serializer = self.get_serializer(data=request.data)
        # 유효한지 검사를 한다
        serializer.is_valid(raise_exception=True)
        # 검증된 데이터를 기반으로 Review 모델 인스턴스를 생성하고 저장한다.
        review = serializer.save()

        # Likes 선택 여부를 확인하고 Review_Likes, Likes_Restaurant에 자동으로 저장
        likes_data = request.data.get('all_likes_list', [])
        i = 0
        for like_id in likes_data:
            # 각각의 likes_Restaurant에서 likes의 pk를 얻는다.
            if int(like_id) == 1:
                try:
                    # Likes_Restaurant의 객체 중 restaurant가 review.restaurant인 것들을 가져옴
                    like = Likes_Restaurant.objects.filter(restaurant=review.restaurant).order_by('pk')[i]
                    i += 1
                    # Review_Likes와 Likes_Restaurant에 저장
                    Review_Likes.objects.create(review=review, likes=like.likes)
                except (ValueError, Likes_Restaurant.DoesNotExist, IndexError):
                    pass
            else:
                i+=1

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
                       

        
        if restaurant_base.name in translated_restaurants_name:
            restaurant_base.name = translated_restaurants_name[restaurant_name]
        else:
            restaurant_base.name = translate_and_extract(restaurant_base.name) 