from unittest.mock import patch
import json

from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.db.utils import  IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.test import APIClient, APITestCase
# Create your tests here.
from .models import (WalletPlatform, UserPlatform, Movements)
from .signals import updateUserPlatformBalance
from .exceptions import ExceptionsMessages, NotFundAvailableException

class UserWalletRegisterTestCase(TestCase):

    def setUp(self):
        User.objects.create(
            email='gjavilae@gmail.com',
            password='123451235@@@'
        )
        WalletPlatform.objects.bulk_create([
            WalletPlatform(name='Cuenta Bancaria', description='Cuenta en algun banco nacional', type='BANCO'),
            WalletPlatform(name='PayPal', description='Cuente en la plataforma PayPal', type='E-WALLET')
        ])

    def test_user_is_correctly_creted(self):
        user = User.objects.first()
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, 'gjavilae@gmail.com')

    def test_create_wallet_platform(self):
        wallet = WalletPlatform.objects.all()
        self.assertIsInstance(wallet[::1], list)
        self.assertEqual(wallet[0].name, 'Cuenta Bancaria')
        
        
    def test_user_has_wallet_error(self):
        wallet = WalletPlatform.objects.first()
        user = User.objects.first()
        with self.assertRaises(IntegrityError):
            platform = UserPlatform.objects.create()

    def test_user_has_wallet_no_error(self):
        wallet = WalletPlatform.objects.first()
        user = User.objects.first()

        platform = UserPlatform.objects.create(
            user=user,
            wallet=wallet,
            description='Mi cuenta en banco de venezuela',
            account='01020145023419'
        )

        self.assertIsNotNone(platform)
        self.assertEqual(platform.wallet.name, wallet.name)
        self.assertIsInstance(platform.wallet, WalletPlatform)
        self.assertEqual(platform.wallet, wallet)


class CorrectUserPlatformTestCase(APITestCase):

    def setUp(self):
        self.wallet = WalletPlatform.objects.create(
            name='Banco De Venezuela',
            description='Banco de venezuela',
            type=WalletPlatform.PLATFORM_TYPE.BANCO
        )
        self.user = User.objects.create(
            email='gjavilae@gmail.com',
            password='123451235@@@'
        )

        self.userPlatform = UserPlatform.objects.create(
            wallet=self.wallet,
            user=self.user,
            description='Mi cuenta de banco de venezuela',
            account='0102014502363899'
        )

    def test_check_instances(self):
        self.assertIsNotNone(self.user)
        self.assertIsNotNone(self.wallet)
        self.assertIsNotNone(self.userPlatform)
        self.assertEqual(self.userPlatform.account, '0102014502363899')
    
    def test_valid_platform_relatd_name(self):
        wallet = WalletPlatform.objects.first()
        user = User.objects.first()

        self.assertIsNotNone(wallet)
        self.assertIsNotNone(user)

        self.assertIsNotNone(wallet.wallet_belongs_user.first())
        self.assertIsInstance(wallet.wallet_belongs_user.first(), UserPlatform)
        self.assertEqual(wallet.wallet_belongs_user.first(), self.userPlatform)
        self.assertEqual('0102014502363899', wallet.wallet_belongs_user.first().account)

    def test_manager(self):
        querySetResult_usingId = UserPlatform.objects.get_by_user(self.user.id)
        querySetResult_usingObject = UserPlatform.objects.get_by_user(self.user)

        self.assertEqual(querySetResult_usingId.count(), 1)
        self.assertEqual(querySetResult_usingObject.count(), 1)
        self.assertEqual(querySetResult_usingId.first().id, querySetResult_usingObject.first().id)


class MovementsTestCase(TestCase):

    def setUp(self):
        self.wallet = WalletPlatform.objects.create(
            name='Banco De Venezuela',
            description='Banco de venezuela',
            type=WalletPlatform.PLATFORM_TYPE.BANCO
        )
        self.user = User.objects.create(
            email='gjavilae@gmail.com',
            password='123451235@@@'
        )

        self.userPlatform = UserPlatform.objects.create(
            wallet=self.wallet,
            user=self.user,
            description='Mi cuenta de banco de venezuela',
            account='0102014502363899'
        )

    def test_create_movements_without_funds(self): 
        with self.assertRaisesRegex(NotFundAvailableException, ExceptionsMessages.NOT_FUND_AVAILABLE ):
            movement = Movements.objects.create(
                platform_user=self.userPlatform,
                description='Transferencia por pago de pastelito',
                amount=50000,
                platform_reference='090532',
                status=Movements.MOVEMENT_STATUS.completed,
                movement_type=Movements.MOVEMENT_TYPE.debit
            )

        

    def test_create_movement(self):
        movement = Movements.objects.create(
            platform_user=self.userPlatform,
            description='Transferencia por pago de pastelito',
            amount=50000,
            platform_reference='090532',
            status=Movements.MOVEMENT_STATUS.completed,
            movement_type=Movements.MOVEMENT_TYPE.credit
        )

        self.assertIsInstance(movement, Movements)
        self.assertIsInstance(movement.platform_user, UserPlatform)

    def test_manager_filter_by_user(self):
        movement = Movements.objects.create(
            platform_user=self.userPlatform,
            description='Transferencia por pago de pastelito',
            amount=50000,
            platform_reference='090532',
            status=Movements.MOVEMENT_STATUS.completed,
            movement_type=Movements.MOVEMENT_TYPE.credit
        )

        querySetResult = Movements.objects.get_by_user(self.userPlatform.user.id)
        self.assertEqual(querySetResult.count(), 1)
        self.assertEqual(querySetResult.first().platform_user.user.id, self.userPlatform.user.id)

class SignalsTestCase(TestCase):

    def setUp(self):
        self.wallet = WalletPlatform.objects.create(
            name='Banco De Venezuela',
            description='Banco de venezuela',
            type=WalletPlatform.PLATFORM_TYPE.BANCO
        )
        self.user = User.objects.create(
            email='gjavilae@gmail.com',
            password='123451235@@@'
        )

        self.userPlatform = UserPlatform.objects.create(
            wallet=self.wallet,
            user=self.user,
            description='Mi cuenta de banco de venezuela',
            account='0102014502363899'
        )

    def test_updateUserPlatformBalance_is_correctly_called(self):
        Movements.objects.create(
            platform_user=self.userPlatform,
            description='Transferencia por pago de pastelito',
            amount=50000,
            platform_reference='090532',
            status=Movements.MOVEMENT_STATUS.completed,
            movement_type=Movements.MOVEMENT_TYPE.credit
        )

        Movements.objects.create(
            platform_user=self.userPlatform,
            description='Transferencia por pago de pastelito',
            amount=10000,
            platform_reference='090533',
            status=Movements.MOVEMENT_STATUS.completed,
            movement_type=Movements.MOVEMENT_TYPE.credit
        )
        platformUser = UserPlatform.objects.first()

        self.assertEqual( platformUser.current_balance, 60000 )


    def test_updateUserPlatformBalance_is_correctly_called_and_debit_movement(self):   
        Movements.objects.create(
            platform_user=self.userPlatform,
            description='Transferencia por pago de pastelito',
            amount=10000,
            platform_reference='090533',
            status=Movements.MOVEMENT_STATUS.completed,
            movement_type=Movements.MOVEMENT_TYPE.credit
        )    

        Movements.objects.create(
            platform_user=self.userPlatform,
            description='Transferencia por pago de pastelito',
            amount=5000,
            platform_reference='090533',
            status=Movements.MOVEMENT_STATUS.completed,
            movement_type=Movements.MOVEMENT_TYPE.debit
        )

        platformUser = UserPlatform.objects.first()
        self.assertEqual(platformUser.current_balance, 5000)



class WalletPlatformTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()    
        self.wallet = WalletPlatform.objects.create(
            name='Banco De Venezuela',
            description='Banco de venezuela',
            type=WalletPlatform.PLATFORM_TYPE.BANCO
        )

        self.user = User.objects.create(
            email='gjavilae@gmail.com',
            password='123451235@@@'
        )
        self.client.force_authenticate(user=self.user)

    
    def test_status_code_ok(self):
        response = self.client.get( reverse('list-wallet-platforms') )
        self.assertEqual(response.status_code, 200)
    
    def test_response_json_void(self):
        response = self.client.get( reverse('list-wallet-platforms') )
        response_content = response.json()


        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response_content, list)

    def test_response_json_with_content(self):
        WalletPlatform.objects.create(
            name='Banco De Venezuela',
            description='Cuentas en el banco de venezuela',
            type=WalletPlatform.PLATFORM_TYPE.BANCO
        )

        response = self.client.get( reverse('list-wallet-platforms') )
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual( len(response_data), 1 )
        self.assertEqual(response_data[0].get('name'), 'Banco De Venezuela')

    def test_create_user_platfrom(self):
        """
            Test create new user wallet, making POST request
        """
        response = self.client.post( 
            reverse('user-wallet'),
            {'user': 1, 'wallet': 1, 'description': 'Mi cuenta en BDV', 'account': '01020145', 'initial_balance': 40000} 
        )

        response_data = response.json()
        platformUser = UserPlatform.objects.first()

        self.assertTrue(response.status_code in [200, 201])
        self.assertEquals(
        response_data.get('wallet').get('description')
        , 'Banco de venezuela')
        self.assertEqual(response_data.get('description'), 'Mi cuenta en BDV')
        self.assertEqual(platformUser.initial_balance, platformUser.current_balance)
        self.assertEqual(platformUser.initial_balance, float(response_data.get('initial_balance')))


    def test_create_user_platfrom_error(self):
        response = self.client.post( reverse('user-wallet'), {} )
        self.assertTrue(response.status_code in [400, 403])
        self.assertTrue( 'wallet' in response.json() )


class MovementsAPITestCase(APITestCase):
    def setUp(self):
        self.wallet = WalletPlatform.objects.create(
            name='Banco De Venezuela',
            description='Banco de venezuela',
            type=WalletPlatform.PLATFORM_TYPE.BANCO
        )
        self.user = User.objects.create(
            email='gjavilae@gmail.com',
            password='123451235@@@'
        )

        self.userPlatform = UserPlatform.objects.create(
            wallet=self.wallet,
            user=self.user,
            description='Mi cuenta de banco de venezuela',
            account='0102014502363899'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_all_movements(self):
        movement = Movements.objects.create(
            platform_user=self.userPlatform,
            description='Transferencia por pago de pastelito',
            amount=50000,
            platform_reference='090532',
            status=Movements.MOVEMENT_STATUS.completed,
            movement_type=Movements.MOVEMENT_TYPE.credit
        )

        movement = Movements.objects.create(
            platform_user=self.userPlatform,
            description='Transferencia por pago de pastelito',
            amount=5000,
            platform_reference='090532',
            status=Movements.MOVEMENT_STATUS.completed,
            movement_type=Movements.MOVEMENT_TYPE.debit
        )
        response = self.client.get( reverse('movements') )

        self.assertEqual( Movements.objects.all().count() , 2 )
        self.assertTrue(response.status_code in [200, 202, 91])
        self.assertEqual( len( response.json() ) , 2 )

    def test_create_new_movement(self): 
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

        response = self.client.post(reverse('movements'), data, format='json')

        self.assertTrue( response.status_code in [200, 201] ,msg='Status_code es diferente a 200 y 201' )
        self.assertEqual(response.json(), data)


class WalletAPITestCase(APITestCase):
    def setUp(self):
        self.wallet = WalletPlatform.objects.create(
            name='Banco De Venezuela',
            description='Banco de venezuela',
            type=WalletPlatform.PLATFORM_TYPE.BANCO
        )
        self.user = User.objects.create(
            email='gjavilae@gmail.com',
            password='123451235@@@'
        )

        self.userPlatform = UserPlatform.objects.create(
            wallet=self.wallet,
            user=self.user,
            description='Mi cuenta de banco de venezuela',
            account='0102014502363899'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)


    def test_list_wallets(self):
        UserPlatform.objects.create(
            wallet=self.wallet,
            user=self.user,
            description='Mi segunda cuenta de banco de venezuela',
            account='0102014502363898'
        )

        response = self.client.get( reverse('user-wallet') )
        response_data = response.json()
        self.assertEquals(response.status_code, 200)
        self.assertEqual( len(response_data), 2 )
        self.assertEqual( response_data[0].get('account'), '0102014502363899' )
        self.assertEqual( response_data[1].get('description'), 'Mi segunda cuenta de banco de venezuela')

    def test_retrieve_wallet(self):
        movement = Movements.objects.create(
            platform_user=self.userPlatform,
            description='Transferencia por pago de pastelito',
            amount=50000,
            platform_reference='090532',
            status=Movements.MOVEMENT_STATUS.completed,
            movement_type=Movements.MOVEMENT_TYPE.credit
        )
        response = self.client.get(reverse('retrieve-wallet', kwargs={'account':'0102014502363899'}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('wallet').get('name'), self.wallet.name)

        self.assertEquals( len(response.json().get('user_earnings')), 1)
        self.assertEquals( response.json().get('user_earnings')[0].get('description'), 'Transferencia por pago de pastelito' )