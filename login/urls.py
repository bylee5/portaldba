from django.urls import path
from django.contrib.auth import views as auth_views

app_name = 'login'
urlpatterns = [
    # ex: /login/
    path('login/', auth_views.LoginView.as_view(template_name='login/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]