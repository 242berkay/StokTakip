from datetime import datetime, time, timedelta
from decimal import Decimal

from django.db.models import DecimalField, F, Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import (
    Category,
    Customer,
    LedgerEntry,
    Order,
    OrderItem,
    Product,
    StockMovement,
)
from .permissions import IsStaffOrReadOnly
from .serializers import (
    CategorySerializer,
    CustomerSerializer,
    LedgerEntrySerializer,
    OrderSerializer,
    ProductSerializer,
    StockMovementSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    permission_classes = [IsStaffOrReadOnly]


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.select_related('product', 'related_order').all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]


class LedgerEntryViewSet(viewsets.ModelViewSet):
    queryset = LedgerEntry.objects.select_related('customer').all()
    serializer_class = LedgerEntrySerializer
    permission_classes = [IsAuthenticated]


def _period_bounds(period, ref_date):
    if period == 'weekly':
        start = ref_date - timedelta(days=ref_date.weekday())
        end = start + timedelta(days=7)
    elif period == 'monthly':
        start = ref_date.replace(day=1)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1)
        else:
            end = start.replace(month=start.month + 1)
    else:  # daily (default)
        start = ref_date
        end = ref_date + timedelta(days=1)
    return start, end


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('customer', 'created_by').prefetch_related(
        'items'
    )
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def report(self, request):
        period = request.query_params.get('period', 'daily')
        if period not in ('daily', 'weekly', 'monthly'):
            return Response(
                {'detail': "period must be one of: daily, weekly, monthly."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        date_str = request.query_params.get('date')
        if date_str:
            try:
                ref_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'detail': 'date must be in YYYY-MM-DD format.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            ref_date = timezone.localdate()

        start_date, end_date = _period_bounds(period, ref_date)
        tz = timezone.get_current_timezone()
        start = timezone.make_aware(datetime.combine(start_date, time.min), tz)
        end = timezone.make_aware(datetime.combine(end_date, time.min), tz)

        orders = Order.objects.filter(
            status=Order.Status.CONFIRMED,
            date__gte=start,
            date__lt=end,
        )
        revenue = OrderItem.objects.filter(order__in=orders).aggregate(
            total=Sum(
                F('qty') * F('unit_price'),
                output_field=DecimalField(max_digits=16, decimal_places=2),
            )
        )['total'] or Decimal('0')

        return Response(
            {
                'period': period,
                'date': ref_date.isoformat(),
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'order_count': orders.count(),
                'revenue': revenue,
            }
        )
