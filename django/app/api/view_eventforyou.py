# coding=utf-8
# from rest_framework import viewsets
import json
# from rest_framework_swagger import renderers
# from rest_framework.decorators import api_view, renderer_classes

from django.views import View
from .models import Event, SubscribeBrand
from django.http import JsonResponse, HttpResponse
from .serializer_event import EventForYouSerializer


# eventforyou
# @renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
class EventforyouView(View):
    model = Event, SubscribeBrand
    # post : post 로 날라온 유저의 eventforyou 찾아주기
    def post(self, request):
        events = []
        # user id 가 있다
        # serializer = EventForYouSerializer(data= request.data)
        subscribebrands = SubscribeBrand.objects.filter(user=self.data)
        for i in subscribebrands :
            eventforyou = Event.objects.filter(brand=i.name)
            events.append(eventforyou)
        # 로그인 한다
        return JsonResponse({'eventforyou' : events})

    def get(self, request):
        return HttpResponse(request.data)