from django.contrib import admin

from .models import (
    Category,
    Customer,
    LedgerEntry,
    Order,
    OrderItem,
    Product,
    StockMovement,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'category', 'unit', 'cost', 'price', 'is_active']
    list_filter = ['is_active', 'category']
    search_fields = ['sku', 'name']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'created_at']
    search_fields = ['name', 'phone', 'email']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'customer', 'status', 'date', 'created_by']
    list_filter = ['status', 'date']
    search_fields = ['order_no', 'customer__name']
    inlines = [OrderItemInline]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'type', 'qty', 'related_order', 'date']
    list_filter = ['type', 'date']
    search_fields = ['product__name', 'product__sku']


@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ['customer', 'description', 'debit', 'credit', 'date']
    list_filter = ['date']
    search_fields = ['customer__name', 'description']
