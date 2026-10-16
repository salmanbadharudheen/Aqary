from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from products.models import Product


class Order(models.Model):
	status = models.CharField(max_length=20, default='pending')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		indexes = [
			models.Index(fields=['status', 'created_at'], name='order_status_created_idx'),
		]

	def __str__(self):
		return f'Order {self.pk} ({self.status})'


class OrderItem(models.Model):
	order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
	product = models.ForeignKey(
		Product,
		related_name='order_items',
		on_delete=models.PROTECT,
	)
	quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
	unit_price = models.DecimalField(
		max_digits=10,
		decimal_places=2,
		validators=[MinValueValidator(Decimal('0.00'))],
	)

	class Meta:
		indexes = [
			models.Index(fields=['product', 'order'], name='order_item_product_order_idx'),
		]
		constraints = [
			models.CheckConstraint(
				condition=models.Q(quantity__gt=0),
				name='order_item_quantity_positive',
			),
			models.CheckConstraint(
				condition=models.Q(unit_price__gte=0),
				name='order_item_price_nonnegative',
			),
		]

	def __str__(self):
		return f'{self.quantity} x {self.product} (order {self.order_id})'
