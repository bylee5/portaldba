from django.urls import path

from . import views

app_name = 'data_life_cycle'
urlpatterns = [
    # ex: /data_life_cycle/
    path('', views.data_life_cycle, name='data_life_cycle'),
]