from django.urls import path
from utils.views import Set2FASecretView, GetOTPView

urlpatterns = [
    path('<int:pk>/set-2fa-secret/', Set2FASecretView.as_view(), name='set-2fa-secret'),
    path('<int:pk>/otp/', GetOTPView.as_view(), name='get-otp'),
]
