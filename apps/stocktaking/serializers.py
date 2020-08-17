from django.core.serializers.python import Serializer

class WallePlatformSerializer(Serializer):

    def end_object(self, record):
        self.objects.append({
            'id': record._get_pk_val(),
            'name': record.name,
            'description': record.description
        })


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