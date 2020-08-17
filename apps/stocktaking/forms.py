from django.forms import ModelForm
from .models import UserPlatform, WalletPlatform


class UserPlatformModelForm(ModelForm):
    class Meta:
        model = UserPlatform
        fields = ['user', 'wallet', 'description', 'account', 'initial_balance']