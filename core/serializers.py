from decimal import Decimal

from django.db import transaction
from django.db.models import Case, DecimalField, F, Sum, When
from rest_framework import serializers

from .models import (
    Category,
    Customer,
    LedgerEntry,
    Order,
    OrderItem,
    Product,
    StockMovement,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'is_active']


class ProductSerializer(serializers.ModelSerializer):
    stock_on_hand = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'sku',
            'name',
            'category',
            'unit',
            'cost',
            'price',
            'is_active',
            'created_at',
            'stock_on_hand',
        ]
        read_only_fields = ['created_at']

    def get_stock_on_hand(self, obj) -> Decimal:
        result = obj.movements.aggregate(
            total=Sum(
                Case(
                    When(type=StockMovement.Type.OUT, then=-F('qty')),
                    default=F('qty'),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
        )
        return result['total'] or Decimal('0')


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone', 'email', 'address', 'created_at']
        read_only_fields = ['created_at']


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'qty', 'unit_price', 'line_total']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total = serializers.DecimalField(
        max_digits=14, decimal_places=2, read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'order_no',
            'customer',
            'date',
            'status',
            'created_by',
            'items',
            'total',
        ]
        read_only_fields = ['date', 'created_by']

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        request = self.context.get('request')
        if request is not None and request.user.is_authenticated:
            validated_data['created_by'] = request.user

        order = Order.objects.create(**validated_data)

        total = Decimal('0')
        for item_data in items_data:
            item = OrderItem.objects.create(order=order, **item_data)
            total += item.line_total
            StockMovement.objects.create(
                product=item.product,
                type=StockMovement.Type.OUT,
                qty=item.qty,
                related_order=order,
                note=f'Order {order.order_no}',
            )

        LedgerEntry.objects.create(
            customer=order.customer,
            description=f'Order {order.order_no}',
            credit=total,
        )
        return order


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = ['id', 'product', 'type', 'qty', 'related_order', 'note', 'date']
        read_only_fields = ['date']


class LedgerEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerEntry
        fields = ['id', 'customer', 'date', 'description', 'debit', 'credit']
        read_only_fields = ['date']
