from rest_framework import serializers

from .models import Order, OrderItem, Product, Transaction, UserAsset, Wallet


class WalletSerializer(serializers.ModelSerializer):
    # deposit = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Wallet
        fields = ['user', 'order_id', 'balance']


class TransactionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['wallet', 'order', 'transaction_type', 'amount', 'status', 'retrieval_ref_no', 'system_trace_no', 'description']


class TransactionSellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['wallet', 'order', 'transaction_type', 'amount', 'status']
    
    def create(self, validated_data):
        transaction = Transaction.objects.create(**validated_data)
        return transaction
        

class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'category', 'unit', 'price', 'in_stock']


class ProductSellSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['in_stock']
    

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'order', 'name', 'quantity', 'price']

    def create(self, validated_data):
        return OrderItem.objects.create(**validated_data)
    

class CreateOrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'order_id', 'user', 'tax_price', 'total_price', 'order_items']

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)

        for order_item_data in order_items_data:
            OrderItem.objects.create(order=order, **order_item_data)

        return order
    

class SellOrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['user', 'order_id', 'is_sold', 'sold_at', 'order_items']

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)

        for order_item_data in order_items_data:
            OrderItem.objects.create(order=order, **order_item_data)

        return order
    
    def update(self, instance, validated_data):
        order_items_data = validated_data.pop('order_items', [])

        instance.is_sold = validated_data.get('is_sold', instance.is_sold)
        instance.sold_at = validated_data.get('sold_at', instance.sold_at)
        instance.save()

        for order_item_data in order_items_data:
            order_item_data.pop('order', None)
            OrderItem.objects.create(order=instance, **order_item_data)
        
        return instance


class UserAssetSerializer(serializers.ModelSerializer):
    sell = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = UserAsset
        fields = ['user', 'product', 'quantity', 'sell']

        extra_kwargs = {
            'user': {'required': False},
            'product': {'required': False}
        }