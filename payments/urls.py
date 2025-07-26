from django.urls import path

from payments import views

urlpatterns = [
    path('verify-payment', views.ZarinpalCallbackView.as_view(), name="zarinpal-callback"),

    path('orders/create/', views.OrderCreateAPIView.as_view(), name='make_order'),
    path('orders/<int:id>/', views.OrderDetailAPIView.as_view(), name='order_detail'),
    path('request-payment/<int:order_id>/', views.RequestPaymentView.as_view(), name='request_payment'),
    path('game-orders/create/', views.GameOrderCreate.as_view(), name='make_game_order'),
    path('game-orders/<int:order_id>/assign-drgame-delivery/', views.AssignDeliveryToDrGame.as_view(),
         name='assign_delivery_to_drgame'),

]
