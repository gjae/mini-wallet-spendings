from django.urls import path, re_path
from django.core import serializers

from .views import (
    PlatformManagement, 
    UserPlatformView,
    UserMovementsView,
    UserPlatformRetrieve
)

urlpatterns = [
    path('', PlatformManagement.as_view(), name='list-wallet-platforms'),
    path('wallets/', UserPlatformView.as_view(), name='user-wallet'),
    path('wallets/<str:account>/', UserPlatformRetrieve.as_view(), name='retrieve-wallet'),
    path('movements/', UserMovementsView.as_view(), name='movements'),
]