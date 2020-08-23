from rest_framework import mixins, generics, response
from rest_framework import permissions

from .models import WalletPlatform, UserPlatform, Movements
from .serializers import (
    WallePlatformSerializer, 
    UserPlatformModelSerializer, 
    UserPlatformModelCreateSerializer,
    MovementSerializer,
    UserPlatformRetrieveSerializer)

class PlatformManagement(generics.ListAPIView):

    queryset = WalletPlatform.objects.all()
    serializer_class = WallePlatformSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class UserPlatformView(generics.CreateAPIView, 
                        mixins.ListModelMixin):

    serializer_class = UserPlatformModelCreateSerializer 
    queryset = []

    def get_queryset(self):
        queryset = super(UserPlatformView, self).get_queryset()
        queryset = UserPlatform.objects.get_by_user(self.request.user) # TODO
        return queryset

    def perform_create(self, serializer): 
        return serializer.save()

    def create(self, request, *args, **kwrgs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create( serializer )

        instance_serializer = UserPlatformModelSerializer(instance)

        return response.Response(instance_serializer.data)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args,**kwargs)


class UserPlatformRetrieve(generics.RetrieveAPIView):

    serializer_class = UserPlatformRetrieveSerializer
    lookup_field = 'account'
    queryset = []
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super(UserPlatformRetrieve, self).get_queryset()
        queryset = UserPlatform.objects.get_by_user(self.request.user)
        return queryset

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class UserMovementsView(generics.GenericAPIView, 
                        mixins.CreateModelMixin,
                        mixins.ListModelMixin):


        permission_classes = [permissions.IsAuthenticated]
        serializer_class = MovementSerializer

        queryset = []
        
        def get_queryset(self, *args, **kwargs):
            queryset = super(UserMovementsView, self).get_queryset(*args,**kwargs)
            
            if( self.request.user is not None ):
                queryset = Movements.objects.get_by_user(self.request.user.id)
            else:
                queryset = Movements.objects.all()
            return queryset

        def get(self, request, *args, **kwargs):
            return self.list(request, *args, **kwargs)

        def post(self, request, *args, **kwargs):
            return self.create(request, *args, **kwargs)