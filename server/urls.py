from django.urls import path

from . import views

app_name = 'server'
urlpatterns = [
    # ex: /server/
    path('', views.server, name='server'),
    path('server_remove', views.server_remove, name='server_remove'),
    path('select', views.server_select, name='server_select'),
    path('dummy', views.server_dummy, name='server_dummy'),
    path('insert', views.server_insert, name='server_insert'),
    
]