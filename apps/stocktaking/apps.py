from django.apps import AppConfig


class StocktakingConfig(AppConfig):
    name = 'stocktaking'

    def ready(self, *args, **kwargs):
        from .signals import *