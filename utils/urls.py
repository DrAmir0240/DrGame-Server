from django.urls import path, include
from rest_framework.routers import DefaultRouter

from utils import views
from utils.views import Set2FASecretView, GetOTPView, SonyAccountViewSet

send_to_tel_view = views.SonyAccountViewSet.as_view({
    'post': 'send_to_telegram',
})
urlpatterns = [
    path('add-new/', views.SonyAccountAdd.as_view(), name='add-new-sony-account'),
    path('add-new/file', views.SonyAccountAddFromFile.as_view(), name='add-new-sony-account-from-file'),
    path('<int:pk>/set-2fa-secret/', views.Set2FASecretView.as_view(), name='set-2fa-secret'),
    path('<int:pk>/otp/', views.GetOTPView.as_view(), name='get-otp'),
    path('accounts-matched-with-order/<int:order_id>/', views.SonyAccountByGameOrderView.as_view(),
         name='sony-account-by-order-games'),
    path('orders-matched-with-sony-accounts/<int:sony_account_id>/', views.GameOrdersBySonyAccountView.as_view(),
         name='sony-account-by-order-games'),
    path('send-to-tel/<int:pk>/send-to-telegram/', send_to_tel_view, name='send-to-tel'),
]
