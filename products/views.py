from rest_framework import mixins, viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Product
from .serializers import ProductSerializer


class ProductPagination(PageNumberPagination):
	page_size = 20


class ProductViewSet(
	mixins.CreateModelMixin,
	mixins.ListModelMixin,
	mixins.RetrieveModelMixin,
	mixins.UpdateModelMixin,
	mixins.DestroyModelMixin,
	viewsets.GenericViewSet,
):
	queryset = Product.objects.all().order_by('id')
	serializer_class = ProductSerializer
	pagination_class = ProductPagination

	def perform_destroy(self, instance):
		if instance.order_items.exists():
			instance.is_active = False
			instance.save(update_fields=['is_active', 'updated_at'])
		else:
			instance.delete()
