from django.core import serializers
from django.http import JsonResponse
from django.views.generic.list import ListView
from django.views import View

from .models import WalletPlatform, UserPlatform
from .serializers import WallePlatformSerializer, WalletSerializer
from .forms import UserPlatformModelForm

class PlatformManagement(ListView):

    model = WalletPlatform
    paginate_by = 100

    def get_queryset(self):
        return WalletPlatform.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = WallePlatformSerializer()

        data = serializer.serialize(queryset)

        return JsonResponse(data, status=200, safe=False)


class CreateUserPlatformView(View):

    http_method_names = ['post', 'options']

    def post(self, request, *args, **kwrgs):

        form = UserPlatformModelForm(request.POST)
        if not form.is_valid():
            return JsonResponse(form.errors, status=400)
        obj = form.save()

        serialize = WalletSerializer()


        return JsonResponse(serialize.serialize([obj]), safe=False)
