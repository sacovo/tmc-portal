from django.apps import AppConfig
from address.apps import AddressConfig


class TMCConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tmc'


class AddressConfig(AddressConfig):
    default_auto_field = 'django.db.models.AutoField'
