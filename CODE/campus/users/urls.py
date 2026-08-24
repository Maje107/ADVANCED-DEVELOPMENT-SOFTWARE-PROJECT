from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views

app_name = 'users'

urlpatterns = [
    path('health', views.HealthCheck.as_view(), name='health'),
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', views.LoginView.as_view(), name='login'),
    path('me', views.MeView.as_view(), name='me'),
    path('forgot-password', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password', views.ResetPasswordView.as_view(), name='reset_password'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerifyView.as_view(), name='token_verify'),
]

