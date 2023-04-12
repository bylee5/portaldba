from django.urls import path

from . import views

app_name = 'process_check'
urlpatterns = [
    # ex: /process_check/
    path('', views.process_check, name='process_check'),
    
]