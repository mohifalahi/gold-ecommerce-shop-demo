from django.contrib import admin

from .models import *

admin.site.register((Wallet, Product, Order, OrderItem, Transaction, UserAsset))
