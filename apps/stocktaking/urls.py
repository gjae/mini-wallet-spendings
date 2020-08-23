from django.urls import path
from django.core import serializers

from .views import (
    PlatformManagement, 
    UserPlatformView,
    UserMovementsView
)

urlpatterns = [
    path('', PlatformManagement.as_view(), name='list-wallet-platforms'),
    path('create-wallet/', UserPlatformView.as_view(), name='create-new-wallet'),
    path('movements/', UserMovementsView.as_view(), name='movements'),
]