from django.urls import path

from users import views

urlpatterns = [
    path('create-api-key/', views.CreateAPIKeyView.as_view(), name='create-api-key'),
    path('request-otp/', views.RequestOTPView.as_view(), name='request-otp'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('auth/status/', views.UserStatusView.as_view(), name='user_status'),
    path('refresh-token/', views.RefreshTokenView.as_view(), name='refresh-token'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
