from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'sku',
            'category',
            'category_name',
            'quantity',
            'unit_price',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
