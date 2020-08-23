from django.core.serializers.python import Serializer
from rest_framework import serializers

from .models import WalletPlatform,UserPlatform

class WallePlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletPlatform
        fields = [ 'id', 'name', 'description' ]

class UserPlatformModelSerializer(serializers.ModelSerializer):
    wallet = WallePlatformSerializer(many=False)
    initial_balance = serializers.DecimalField(max_digits=23, decimal_places=2)
    class Meta:
        model = UserPlatform
        fields = ['user', 'wallet', 'description', 'account', 'initial_balance']

class UserPlatformModelCreateSerializer(serializers.ModelSerializer):
    initial_balance = serializers.DecimalField(max_digits=23, decimal_places=2)
    class Meta:
        model = UserPlatform
        fields = ['user', 'wallet', 'description', 'account', 'initial_balance']


class WalletSerializer(Serializer):

    def end_object(self, record):
        self.objects.append({
            'id': record.id,
            'account': record.account,
            'initial_balance': record.initial_balance,
            'current_balance': record.current_balance,
            'description': record.description,
            'wallet': {
                'id': record.wallet.id,
                'name': record.wallet.name,
                'description': record.wallet.description
            }
        })