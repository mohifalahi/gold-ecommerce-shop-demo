from django.urls import path

from base.views import order

urlpatterns = [
    path('create-order/', order.OrderCreateAPIView.as_view(), name='create-order'),
    path('cart/', order.CartDetailAPIView.as_view(), name='cart'),
    path('online-pay-order/<uuid:id>/', order.OnlinePayOrderAPIView.as_view(), name='online-pay-order'),
    path('payment-result/', order.OrderPaymentResultAPIView.as_view(), name='order-payment-result'),
    path('<int:pk>/sell-order/<int:asset_id>/', order.SellOrderAPIView.as_view(), name='sell-order'),
]