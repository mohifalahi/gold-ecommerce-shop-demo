from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from base.models import Transaction
from base.pagination import CustomPagination
from base.serializers import TransactionListSerializer


class TransactionListAPIView(generics.ListAPIView):
    
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionListSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        queryset = Transaction.objects.filter(order__user=user_id).order_by('id')
        return queryset