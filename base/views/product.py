from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from base.models import Product
from base.pagination import CustomPagination
from base.serializers import ProductListSerializer


class ProductListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductListSerializer
    queryset = Product.objects.all().order_by('id')
    pagination_class = CustomPagination