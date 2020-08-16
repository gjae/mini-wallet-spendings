from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth.models import User
from django.db.utils import  IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver
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


class CorrectUserPlatformTestCase(TestCase):

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
