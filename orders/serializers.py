from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemInputSerializer(serializers.Serializer):
	product_id = serializers.IntegerField(min_value=1)
	quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
	items = OrderItemInputSerializer(many=True, allow_empty=False)


class OrderItemSerializer(serializers.ModelSerializer):
	product_id = serializers.IntegerField(read_only=True)

	class Meta:
		model = OrderItem
		fields = ['id', 'product_id', 'quantity', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
	items = OrderItemSerializer(many=True, read_only=True)

	class Meta:
		model = Order
		fields = ['id', 'status', 'created_at', 'items']