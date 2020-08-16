from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

from model_utils import  Choices
from model_utils.models import TimeStampedModel, StatusModel

from .exceptions import ExceptionsMessages, NotFundAvailableException
# Create your models here.

class WalletPlatform(TimeStampedModel):

    PLATFORM_TYPE = Choices('BANCO', 'E-WALLET', 'CRYPTOCURRENCY')

    name = models.CharField(max_length=150, null=False, blank=False)
    description= models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(choices=PLATFORM_TYPE, max_length=30)

    def __str__(self):
        return self.name



class UserPlatform(StatusModel):
    STATUS = Choices('active', 'trash')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_has_wallet')
    wallet = models.ForeignKey(WalletPlatform, on_delete=models.CASCADE, related_name='wallet_belongs_user')
    description = models.CharField(max_length=90, blank=True)
    account = models.CharField(max_length=99, default='--', null=False, blank=False)
    initial_balance = models.DecimalField(max_digits=23, decimal_places=2, default=0.00)
    spent_total_balance = models.DecimalField(max_digits=23, decimal_places=2, default=0.00)
    earning_total_balance = models.DecimalField(max_digits=23, decimal_places=2, default=0.00)
    current_balance= models.DecimalField(max_digits=23, decimal_places=2, default=0.00)

    last_movement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{0} - {1}'.format(self.wallet.name, self.description)



class Movements(TimeStampedModel):

    """
        Model that define movements on someone user account
    """

    MOVEMENT_STATUS = Choices('completed', 'deferred', 'blocked')
    MOVEMENT_TYPE = Choices('credit', 'debit')

    platform_user = models.ForeignKey(UserPlatform, on_delete=models.CASCADE, related_name='user_earnings')
    description = models.CharField(max_length=190, blank=True, null=True)
    amount = models.DecimalField(max_digits=23, decimal_places=2, null=False)
    platform_reference = models.CharField(max_length=15, blank=False, null=False)

    status = models.CharField(max_length=20, choices=MOVEMENT_STATUS, default=MOVEMENT_STATUS.completed)
    movement_type = models.CharField(max_length=15, choices=MOVEMENT_TYPE, blank=False, null=False)

    class Meta:
        indexes = [
            models.Index(fields=['platform_reference', ], name='platform_reference_index')
        ]


    def __str__(self):
        return '{0} - {1}'.format(self.platform_user.wallet.name)

    def  save(self, *args, **kwargs):
        if (
            self.movement_type == self.MOVEMENT_TYPE.debit and 
            self.platform_user.current_balance < self.amount
        ):
            raise NotFundAvailableException(ExceptionsMessages.NOT_FUND_AVAILABLE)

        super(Movements, self).save(*args, **kwargs)

