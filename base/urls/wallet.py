from django.urls import path

from base.views import wallet

urlpatterns = [
    path('wallet-deposit/<int:pk>/', wallet.WalletDepositView.as_view(), name='wallet-deposit'),
    path('payment-result/', wallet.WalletPaymentResultAPIView.as_view(), name='wallet-payment-result'),
    path('<int:pk>/pay-order/<uuid:id>/', wallet.WalletPayOrderAPIView.as_view(), name='wallet-pay-order'),
]