from django.urls import path

from base.views import product

urlpatterns = [
    path('products/', product.ProductListAPIView.as_view(), name='products'),
]