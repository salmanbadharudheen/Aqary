from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
	name = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	price = models.DecimalField(
		max_digits=10,
		decimal_places=2,
		validators=[MinValueValidator(Decimal('0.00'))],
	)
	stock = models.PositiveIntegerField(default=0)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		indexes = [
			models.Index(fields=['is_active', 'created_at'], name='product_active_created_idx'),
		]
		constraints = [
			models.CheckConstraint(
				condition=models.Q(price__gte=0),
				name='product_price_nonnegative',
			),
		]

	def __str__(self):
		return self.name
