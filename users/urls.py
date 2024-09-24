from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CompleteSignupView

urlpatterns = [
    path('signup/', CompleteSignupView.as_view(), name='signup'),
    path('complete_signup/', CompleteSignupView.as_view(), name='complete_signup'),
    path('login/', auth_views.LoginView.as_view(), name='account_login'),  # исправлено имя на 'account_login'
    path('logout/', auth_views.LogoutView.as_view(), name='account_logout'),
]
