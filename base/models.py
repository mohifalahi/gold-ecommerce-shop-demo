import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField

from authentication.models import User


class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    balance = MoneyField(max_digits=20, decimal_places=2, default_currency='IRR')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    name = models.CharField(max_length=200, null=True)

    CATEGORY_CHOICES = [
        ("18ayar", "18ayar"),
    ]

    UNIT_CHOICES = [
        ("gram", _("gram")),
        ("oz", _("oz")),
        ("quantity", _("quantity"))
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    unit = models.CharField(max_length=8, choices=UNIT_CHOICES)
    price = MoneyField(max_digits=11, decimal_places=2, default_currency='IRR', null=True, blank=True)
    in_stock = models.IntegerField(null=True, blank=True, default=0)
    buy_commission = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    sell_commission = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.CharField(max_length=19, unique=True, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    payment_method = models.CharField(max_length=255, null=True, blank=True)

    tax_price = MoneyField(max_digits=11, decimal_places=2, default_currency='IRR', null=True, blank=True)
    shipping_price = MoneyField(max_digits=11, decimal_places=2, default_currency='IRR', null=True, blank=True)
    total_price = MoneyField(max_digits=11, decimal_places=2, default_currency='IRR', null=True, blank=True)

    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    is_delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    is_sold = models.BooleanField(default=False)
    sold_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)
    
    def get_order_id(self):
        return self.order_id


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True, default=0)
    price = MoneyField(max_digits=11, decimal_places=2, default_currency='IRR', null=True, blank=True)

    def __str__(self):
        return self.name


class UserAsset(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)

    def __str__(self):
        return str(self.id)


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, null=True, blank=True)

    TRANSACTION_TYPE_CHOICES = [
        ("b", "buy"),
        ("s", "sell"),
        ("d", "deposit"),
        ("w", "withdraw")
    ]

    transaction_type = models.CharField(max_length=8, choices=TRANSACTION_TYPE_CHOICES)
    amount = MoneyField(max_digits=20, decimal_places=2, default_currency='IRR', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)
    retrieval_ref_no = models.CharField(max_length=255, null=True, blank=True)
    system_trace_no = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.id)
