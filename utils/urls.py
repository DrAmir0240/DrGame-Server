from django.urls import path, include
from rest_framework.routers import DefaultRouter

from utils.views import Set2FASecretView, GetOTPView, SonyAccountViewSet

router = DefaultRouter()
router.register(r"send-to-tel", SonyAccountViewSet, basename="send-to-tel")
urlpatterns = [
    path('<int:pk>/set-2fa-secret/', Set2FASecretView.as_view(), name='set-2fa-secret'),
    path('<int:pk>/otp/', GetOTPView.as_view(), name='get-otp'),
    path('', include(router.urls)),

]
