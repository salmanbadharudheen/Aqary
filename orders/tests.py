from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from orders.models import Order
from products.models import Product


class OrderAPITests(APITestCase):
	def setUp(self):
		self.first_product = Product.objects.create(
			name='First product',
			description='',
			price=Decimal('12.50'),
			stock=5,
		)
		self.second_product = Product.objects.create(
			name='Second product',
			description='',
			price=Decimal('3.25'),
			stock=1,
		)

	def test_place_and_retrieve_order_preserves_purchase_price(self):
		response = self.client.post(
			reverse('orders:order-list-create'),
			{
				'items': [
					{'product_id': self.first_product.pk, 'quantity': 2},
					{'product_id': self.second_product.pk, 'quantity': 1},
				],
			},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		order_id = response.data['id']
		self.assertEqual(len(response.data['items']), 2)
		self.first_product.refresh_from_db()
		self.second_product.refresh_from_db()
		self.assertEqual(self.first_product.stock, 3)
		self.assertEqual(self.second_product.stock, 0)

		self.first_product.price = Decimal('99.99')
		self.first_product.save(update_fields=['price'])
		retrieval = self.client.get(reverse('orders:order-detail', args=[order_id]))

		self.assertEqual(retrieval.status_code, status.HTTP_200_OK)
		self.assertEqual(retrieval.data['id'], order_id)
		self.assertEqual(
			next(
				item['unit_price']
				for item in retrieval.data['items']
				if item['product_id'] == self.first_product.pk
			),
			'12.50',
		)

	def test_list_orders(self):
		created = self.client.post(
			reverse('orders:order-list-create'),
			{
				'items': [
					{'product_id': self.first_product.pk, 'quantity': 1},
				],
			},
			format='json',
		)

		response = self.client.get(reverse('orders:order-list-create'))

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]['id'], created.data['id'])
		self.assertEqual(response.data[0]['items'][0]['product_id'], self.first_product.pk)

	def test_insufficient_stock_rejects_order_without_changing_any_stock(self):
		response = self.client.post(
			reverse('orders:order-list-create'),
			{
				'items': [
					{'product_id': self.first_product.pk, 'quantity': 2},
					{'product_id': self.second_product.pk, 'quantity': 2},
				],
			},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.first_product.refresh_from_db()
		self.second_product.refresh_from_db()
		self.assertEqual(self.first_product.stock, 5)
		self.assertEqual(self.second_product.stock, 1)
		self.assertEqual(Order.objects.count(), 0)

	def test_zero_quantity_is_rejected(self):
		response = self.client.post(
			reverse('orders:order-list-create'),
			{'items': [{'product_id': self.first_product.pk, 'quantity': 0}]},
			format='json',
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(Order.objects.count(), 0)
