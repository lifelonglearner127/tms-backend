from django.conf.urls import url, include

from rest_framework_nested import routers
from .import views as v

router = routers.SimpleRouter(trailing_slash=False)
router.register(
    r'products',
    v.WarehouseProductViewSet,
    base_name='product'
)
router.register(
    r'in-transactions-history',
    v.InTransactionHistoryViewSet,
    base_name='in-transaction-history'
)
router.register(
    r'out-transactions-history',
    v.OutTransactionHistoryViewSet,
    base_name='out-transaction-history'
)
router.register(
    r'export/in-transactions-history', v.InTransactionHistoryExportViewSet, base_name='export-in-transaction'
)
router.register(
    r'export/out-transactions-history', v.OutTransactionHistoryExportViewSet, base_name='export-out-transaction'
)

# # /products/{product_pk}/in_transactions
# # /products/{product_pk}/in_transactions/{pk}
transaction_router = routers.NestedSimpleRouter(
    router,
    r'products',
    lookup='product'
)
transaction_router.register(
    r'in-transactions',
    v.InTransactionViewSet,
    base_name='in-transaction'
)
transaction_router.register(
    r'out-transactions',
    v.OutTransactionViewSet,
    base_name='out-transaction'
)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(transaction_router.urls)),
]
