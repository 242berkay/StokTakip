from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CustomerViewSet,
    LedgerEntryViewSet,
    OrderViewSet,
    ProductViewSet,
    StockMovementViewSet,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'stock-movements', StockMovementViewSet, basename='stockmovement')
router.register(r'ledger', LedgerEntryViewSet, basename='ledgerentry')

urlpatterns = router.urls
