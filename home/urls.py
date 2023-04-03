from django.urls import path

from . import views

app_name = 'home'
urlpatterns = [
    # ex:
    path('', views.home, name='home'),
]