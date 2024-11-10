from django.urls import path

from base.views import transaction

urlpatterns = [
    path('<int:user_id>/', transaction.TransactionListAPIView.as_view(), name='transactions')
]