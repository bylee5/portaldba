from django.urls import path

from . import views

app_name = 'account'
urlpatterns = [
    # ex: /account/
    path('', views.account, name='account'),
    path('account/select_fast', views.account_select_fast, name='account_select_fast'),
    path('account/account_remove', views.account_remove, name='account_remove'),
       path('account/repository/select', views.account_repository_select, name='account_repository_select'),
]