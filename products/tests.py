from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from orders.models import Order, OrderItem
from .models import Product


class ProductAPITests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.payload = {
			'name': 'Desk lamp',
			'description': 'Adjustable LED desk lamp',
			'price': '29.99',
			'stock': 5,
		}

	def test_create_list_retrieve_and_patch_product(self):
		response = self.client.post('/api/products/', self.payload, format='json')
		self.assertEqual(response.status_code, 201)
		product_id = response.data['id']
		self.assertEqual(response.data['price'], '29.99')

		response = self.client.get('/api/products/')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data['results']), 1)
		self.assertEqual(response.data['results'][0]['id'], product_id)

		response = self.client.get(f'/api/products/{product_id}/')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['name'], 'Desk lamp')

		response = self.client.patch(
			f'/api/products/{product_id}/',
			{'stock': 8},
			format='json',
		)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['stock'], 8)

	def test_rejects_negative_price_and_stock(self):
		for field, value in [('price', '-0.01'), ('stock', -1)]:
			payload = {**self.payload, field: value}
			with self.subTest(field=field):
				response = self.client.post(
					'/api/products/',
					payload,
					format='json',
				)
				self.assertEqual(response.status_code, 400)
				self.assertIn(field, response.data)

	def test_product_list_is_paginated(self):
		Product.objects.bulk_create(
			[
				Product(name=f'Product {index}', price=Decimal('1.00'))
				for index in range(21)
			]
		)

		response = self.client.get('/api/products/')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['count'], 21)
		self.assertEqual(len(response.data['results']), 20)
		self.assertIsNotNone(response.data['next'])

	def test_delete_deactivates_product_referenced_by_order(self):
		product = Product.objects.create(
			name='Desk lamp',
			price=Decimal('29.99'),
			stock=5,
		)
		order = Order.objects.create()
		OrderItem.objects.create(
			order=order,
			product=product,
			quantity=1,
			unit_price=product.price,
		)

		response = self.client.delete(f'/api/products/{product.pk}/')

		self.assertEqual(response.status_code, 204)
		product.refresh_from_db()
		self.assertFalse(product.is_active)

	def test_delete_removes_product_without_order_references(self):
		product = Product.objects.create(
			name='Desk lamp',
			price=Decimal('29.99'),
			stock=5,
		)

		response = self.client.delete(f'/api/products/{product.pk}/')

		self.assertEqual(response.status_code, 204)
		self.assertFalse(Product.objects.filter(pk=product.pk).exists())
