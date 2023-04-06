from django.urls import path

from . import views

app_name = 'server'
urlpatterns = [
    # ex: /server/
    path('', views.server, name='server'),
    path('server_remove', views.server_remove, name='server_remove'),
]