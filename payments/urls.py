from django.urls import path

from payments import views

urlpatterns = [
    path('orders/create/', views.OrderCreateAPIView.as_view(), name='make_order'),
    path('orders/<int:id>/', views.OrderDetailAPIView.as_view(), name='order_detail'),
    path('request-payment/<int:order_id>/', views.RequestPaymentView.as_view(), name='request_payment'),
    path("verify-payment", views.ZarinpalCallbackView.as_view(), name="zarinpal-callback"),

]
