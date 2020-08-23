from rest_framework import serializers

from .models import WalletPlatform,UserPlatform, Movements

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
    class Meta:
        model = UserPlatform
        fields = ['user', 'wallet', 'description', 'account', 'initial_balance']

class MovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movements
        fields = ['platform_user', 'description', 'amount', 'platform_reference', 'status', 'movement_type']


class UserPlatformRetrieveSerializer(serializers.ModelSerializer):
    wallet = WallePlatformSerializer(many=False, read_only=True)
    user_earnings = MovementSerializer(many=True,  read_only=True)
    class Meta:
        model = UserPlatform
        fields = ['user', 'wallet', 'user_earnings','description', 'account', 'initial_balance', 'spent_total_balance', 'earning_total_balance', 'current_balance', 'last_movement']

