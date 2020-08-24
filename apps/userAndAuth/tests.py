from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from oauth2_provider.settings import oauth2_settings
from oauth2_provider.models import get_access_token_model, get_application_model
# Create your tests here.
from rest_framework.test import APIClient, APITestCase

from apps.stocktaking.models import UserPlatform, WalletPlatform,Movements

Application = get_application_model()
AccessToken = get_access_token_model()
UserModel = get_user_model()

class UserAuthenticationTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = UserModel.objects.create_user("test_user", "test@example.com", "123456")
        self.application = Application.objects.create(
            name='Test Application',
            redirect_uris='http://localhost:8000',
            user=self.test_user,
            client_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        self.access_token = AccessToken.objects.create(
            user=self.test_user,
            scope='*',
            expires=timezone.now() + timezone.timedelta(seconds=300),
            token="test-token-secret",
            application=self.application
        )
        self.access_token.scope = "read"
        self.access_token.save()

        # correct token and correct scope
        self.auth =  "Bearer {0}".format(self.access_token.token)
        self.wallet = WalletPlatform.objects.create(
            name='Banco De Venezuela',
            description='Banco de venezuela',
            type=WalletPlatform.PLATFORM_TYPE.BANCO
        )
        self.userPlatform = UserPlatform.objects.create(
            wallet=self.wallet,
            user=self.test_user,
            description='Mi cuenta de banco de venezuela',
            account='0102014502363899'
        )

    def test_oauth_token_error(self):
        movement = Movements.objects.create(
            platform_user=self.userPlatform,
            description='Transferencia por pago de pastelito',
            amount=50000,
            platform_reference='090532',
            status=Movements.MOVEMENT_STATUS.completed,
            movement_type=Movements.MOVEMENT_TYPE.credit
        )
        data = {
            'platform_user': 1, 
            "description": "Pago realizado a alguien", 
            "amount": 10000,
            "platform_reference": '00901903',
            "status": Movements.MOVEMENT_STATUS.completed,
            "movement_type": Movements.MOVEMENT_TYPE.debit
        }

        response = self.client.post(
            reverse('movements'), data, format='json', HTTP_AUTHORIZATION='Bearer TEST-ERROR-TOKEN'
        )
        

        self.assertEqual(response.status_code, 401, msg='This test should fail because API Token is incorrect')

    
    def test_oauth_token_on_create_movement(self):
        movement = Movements.objects.create(
            platform_user=self.userPlatform,
            description='Transferencia por pago de pastelito',
            amount=50000,
            platform_reference='090532',
            status=Movements.MOVEMENT_STATUS.completed,
            movement_type=Movements.MOVEMENT_TYPE.credit
        )
        data = {
            'platform_user': 1, 
            "description": "Pago realizado a alguien", 
            "amount": 10000,
            "platform_reference": '00901903',
            "status": Movements.MOVEMENT_STATUS.completed,
            "movement_type": Movements.MOVEMENT_TYPE.debit
        }

        response = self.client.post(
            reverse('movements'), data, format='json', HTTP_AUTHORIZATION=self.auth
        )

        self.assertTrue( response.status_code in [200, 201] ,msg='Status_code es diferente a 200 y 201' )
        self.assertEqual(response.json(), data)
