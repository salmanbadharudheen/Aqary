from django.db import transaction

from products.models import Product

from .models import Order, OrderItem


class OrderPlacementError(Exception):
	pass


def place_order(items):
	if not isinstance(items, list) or not items:
		raise OrderPlacementError('An order must contain at least one item.')

	requested_quantities = {}
	for item in items:
		if not isinstance(item, dict):
			raise OrderPlacementError('Each item must be an object.')

		product_id = item.get('product_id')
		quantity = item.get('quantity')
		if type(product_id) is not int or product_id <= 0:
			raise OrderPlacementError('Each product_id must be a positive integer.')
		if type(quantity) is not int or quantity <= 0:
			raise OrderPlacementError('Each quantity must be a positive integer.')

		requested_quantities[product_id] = (
			requested_quantities.get(product_id, 0) + quantity
		)

	with transaction.atomic():
		products = list(
			Product.objects.select_for_update()
			.filter(pk__in=requested_quantities)
			.order_by('pk')
		)
		products_by_id = {product.pk: product for product in products}
		missing_ids = set(requested_quantities) - set(products_by_id)
		if missing_ids:
			missing = ', '.join(str(product_id) for product_id in sorted(missing_ids))
			raise OrderPlacementError(f'Products do not exist: {missing}.')

		for product in products:
			quantity = requested_quantities[product.pk]
			if product.stock < quantity:
				raise OrderPlacementError(
					f'Insufficient stock for product {product.pk}.'
				)

		order = Order.objects.create()
		OrderItem.objects.bulk_create([
			OrderItem(
				order=order,
				product=product,
				quantity=requested_quantities[product.pk],
				unit_price=product.price,
			)
			for product in products
		])

		for product in products:
			product.stock -= requested_quantities[product.pk]
			product.save(update_fields=['stock', 'updated_at'])

	return order