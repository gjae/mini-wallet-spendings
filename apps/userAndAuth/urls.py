from django.urls import path, include

urlpatterns = [
    path('', include('oauth2_provider.urls', namespace='oauth2_provider')),    
]