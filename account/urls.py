from django.urls import path

from . import views

app_name = 'account'
urlpatterns = [
    # ex: /account/
    path('', views.account, name='account'),
    path('select_fast', views.account_select_fast, name='account_select_fast'),
    path('account_remove', views.account_remove, name='account_remove'),
    path('repository/select', views.account_repository_select, name='account_repository_select'),
    path('account_dummy_pass', views.account_dummy_pass, name='account_dummy_pass'),
    path('multi_dml', views.account_multi_dml, name='account_multi_dml'),
    path('account_search_sql_list', views.account_search_sql_list, name='account_search_sql_list'),
    path('insert', views.account_insert, name='account_insert'),
    path('delete', views.account_delete, name='account_delete'),
    path('update', views.account_update, name='account_update'),
    path('select', views.account_select, name='account_select'),
    path('dummy', views.account_dummy, name='account_dummy'),
    # account Repository Manage 
    path('repository', views.account_repository, name='account_repository'),
    path('repository_select', views.account_repository_select, name='account_repository_select'),
    path('repository_insert', views.account_repository_insert, name='account_repository_insert'),
    path('repository_update', views.account_repository_update, name='account_repository_update'),
    # account remove
    path('account_remove', views.account_remove, name='account_remove'),
    path('account_remove_select', views.account_remove_select, name='account_remove_select'),
    path('account_remove_recover_account_list', views.account_remove_recover_account_list, name='account_remove_recover_account_list'),
]