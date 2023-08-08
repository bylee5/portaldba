from django.urls import path

from . import views

app_name = 'memo'
urlpatterns = [
    # ex: /memo/
    path('', views.memo, name='memo'),
    path('<int:memo_id>/',views.memo_select, name='memo_select'),
    path('insert',views.memo_insert, name='memo_insert'),
]