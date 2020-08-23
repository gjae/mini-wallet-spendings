from django.core import serializers
from django.http import JsonResponse
from django.views.generic.list import ListView
from django.views import View

from rest_framework import mixins, generics, response

from .models import WalletPlatform, UserPlatform
from .serializers import (
    WallePlatformSerializer, 
    WalletSerializer, 
    UserPlatformModelSerializer, 
    UserPlatformModelCreateSerializer)

from .forms import UserPlatformModelForm

class PlatformManagement(generics.ListAPIView):

    queryset = WalletPlatform.objects.all()
    serializer_class = WallePlatformSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CreateUserPlatformView(generics.CreateAPIView):

    serializer_class = UserPlatformModelCreateSerializer

    def perform_create(self, serializer): 
        return serializer.save()

    def create(self, request, *args, **kwrgs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create( serializer )

        instance_serializer = UserPlatformModelSerializer(instance)

        return response.Response(instance_serializer.data)
