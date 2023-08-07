from django.urls import path

from . import views

app_name = 'memo'
urlpatterns = [
    # ex: /memo/
    path('', views.memo, name='memo'),
    path('insert',views.memo_insert, name='memo_insert'),
]