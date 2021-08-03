# coding=utf-8
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.views import APIView

from .models import SubscribeBrand, Brand, User
from .serializer_subscribeBrand import SubscribeBrandSerializer
from django_filters.rest_framework import FilterSet, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# 브랜드 좋아요 버튼, 마이브랜드_브랜드


class SubscribeBrandFilter(FilterSet):
    user = filters.NumberFilter(field_name="user")

    class Meta:
        model = SubscribeBrand
        fields = ['user']


class SubscribeBrandViewSet(viewsets.ModelViewSet):
    '''
        POST /api/mybrands/ - 유저의 브랜드 구독 생성 ( { "user": , "brand": } )
        POST /api/mybrands/users/ - 유저의 마이브랜드 목록을 불러오는 API
        POST /api/guest/mybrand/ - 회원가입 할때 유저의 브랜드 구독 생성
    '''
    serializer_class = SubscribeBrandSerializer
    queryset = SubscribeBrand.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SubscribeBrandFilter

    response_schema_dict2 = {
        "200": openapi.Response(
            description="유저의 마이브랜드 목록을 불러오는 API",
            examples={
                "application/json": {
                    "mybrand": [
                        {
                            "id": 1,
                            "created_date": "2021-07-11",
                            "update_date": "2021-07-28",
                            "category_id": 1,
                            "image": "brand_logo/KakaoTalk_20180520_163620948_CGTwIBG.jpg",
                            "banner_image": "brand_banner/KakaoTalk_20180520_163620948.jpg",
                            "name": "vips",
                            "text": "no1. stake house"
                        },
                        {
                            "id": 3,
                            "created_date": "2021-07-11",
                            "update_date": "2021-07-11",
                            "category_id": 2,
                            "image": "",
                            "banner_image": 'null',
                            "name": "starbucks",
                            "text": "no1. cooffee"
                        }
                    ]
                }
            }
        )
    }

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_NUMBER, description='int')
        }
    ), responses=response_schema_dict2)
    @action(detail=False, methods=['post'])
    def users(self, request):
        """
            유저의 마이브랜드 목록을 불러오는 API

            # header
                - Authorization : jwt ey93..... [jwt token]
            # URL
                - POST /api/mybrands/users/

        """
        data = JSONParser().parse(request)
        user = data['user_id']
        my = SubscribeBrand.objects.filter(user=user).order_by('brand__category', 'brand__name')
        brands = Brand.objects.none()
        for i in my:
            brand = Brand.objects.filter(id=i.brand.id)
            brands = brands.union(brand)
        mybrand = brands.values()
        return JsonResponse({'mybrand': list(mybrand)}, status=200)

    response_schema_dict1 = {
        "200": openapi.Response(
            description="유저의 마이브랜드 구독을 취소하는 API",
            examples={
                "application/json": {
                    "message": "브랜드 구독 취소"
                }
            }
        )
    }
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_NUMBER, description='int'),
            'brand_id': openapi.Schema(type=openapi.TYPE_NUMBER, description='int')
        }
    ), responses=response_schema_dict1)
    @action(detail=False, methods=['post'])
    def unlike(self, request):
        """
            유저 브랜드 구독 취소

            # header
                - Authorization : jwt ey93..... [jwt token]
            # URL
                - POST /api/mybrands/unlike/

        """
        data = JSONParser().parse(request)
        user_id = data['user_id']
        brand_id = data['brand_id']
        subscribe = SubscribeBrand.objects.filter(user=user_id, brand=brand_id)
        subscribe.delete()
        return JsonResponse({"message": "브랜드 구독 취소"}, status=200)

@permission_classes([IsAuthenticated])
class BrandLike(APIView):
    response_schema_dict3 = {
        "200": openapi.Response(
            description="회원가입 선호브랜드때 브랜드 구독하는 API",
            examples={
                "application/json": {
                    "message": "브랜드 구독 성공"
                }
            }
        )
    }

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_NUMBER, description='int'),
            'brand_id': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_NUMBER),
                                       description='int')
        }
    ), responses=response_schema_dict3)
    def post(self, request, format=None):
        """
            회원가입 선호브랜드 할때 브랜드 구독하는 API

            # header
                - 이건 토큰 아니고.. 기본 로그인으로 되나? 고민
            # URL
                - POST /api/guest/mybrands/

        """
        data = JSONParser().parse(request)
        user_id = data['user_id']
        brand_id = data['brand_id']
        for i in brand_id:
            SubscribeBrand.objects.create(user=User.objects.get(id=user_id), brand=Brand.objects.get(id=i))
        return JsonResponse({'message': "브랜드 구독 성공"}, status=200)
