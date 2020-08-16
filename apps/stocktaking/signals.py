from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Movements, UserPlatform

@receiver(post_save, sender=Movements)
def updateUserPlatformBalance(sender, instance, created, *args, **kwargs):
    """
        This signal update balance of the user
    """

    platform_movement = None
    amount = instance.amount
    if created: 
        platform_movement = instance.platform_user
        if instance.movement_type == Movements.MOVEMENT_TYPE.debit:
            platform_movement.current_balance = platform_movement.current_balance - amount;
            platform_movement.spent_total_balance = platform_movement.spent_total_balance + amount
        else: 
            platform_movement.current_balance = platform_movement.current_balance + amount
            platform_movement.earning_total_balance = platform_movement.earning_total_balance + amount

    if platform_movement is not None:
        platform_movement.save()