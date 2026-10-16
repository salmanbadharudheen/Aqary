from django.urls import path
from rest_framework.routers import SimpleRouter

from products.views import ProductViewSet

from .views import health

router = SimpleRouter()
router.register('products', ProductViewSet, basename='product')

urlpatterns = router.urls + [
    path('health/', health, name='health'),
]