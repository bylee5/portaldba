from django.apps import AppConfig

# default_auto_field 설정을 통해 자동으로 증가하는 id 컬럼(PK)을 추가함
class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'
