from django.urls import path
from django.core import serializers

from .views import PlatformManagement, CreateUserPlatformView

urlpatterns = [
    path('', PlatformManagement.as_view(), name='list-wallet-platforms'),
    path('create-wallet/', CreateUserPlatformView.as_view(), name='create-new-wallet')
]