from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=120)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
    )
    unit = models.CharField(max_length=32, default='pcs')
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.sku})'


class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Order(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'

    order_no = models.CharField(max_length=64, unique=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='orders',
    )
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.order_no

    @property
    def total(self):
        return sum((item.line_total for item in self.items.all()), start=0)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items',
    )
    qty = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.product} x {self.qty}'

    @property
    def line_total(self):
        return self.qty * self.unit_price


class StockMovement(models.Model):
    class Type(models.TextChoices):
        IN = 'in', 'In'
        OUT = 'out', 'Out'
        ADJ = 'adj', 'Adjustment'

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='movements',
    )
    type = models.CharField(max_length=8, choices=Type.choices)
    qty = models.DecimalField(max_digits=12, decimal_places=2)
    related_order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movements',
    )
    note = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.get_type_display()} {self.product} {self.qty}'


class LedgerEntry(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='ledger_entries',
    )
    date = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = 'ledger entries'
        ordering = ['-date']

    def __str__(self):
        return f'{self.customer} D:{self.debit} C:{self.credit}'
