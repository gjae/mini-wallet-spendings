from django.db import models


class MovementsManager(models.Manager):

    def get_by_user(self, user_id:int):
        return self.filter(
            platform_user__user=user_id
        )

class UserPlatformManager(models.Manager):

    def get_by_user(self, user):
        return self.filter(
            user=user
        )