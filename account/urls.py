from django.urls import path

from . import views

app_name = 'account'
urlpatterns = [
    # ex: /account/
    path('', views.index, name='index'),
]