from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import OrderCreateSerializer, OrderSerializer
from .services import OrderPlacementError, place_order


class OrderListCreateView(APIView):
	def get(self, request):
		orders = Order.objects.prefetch_related('items__product').order_by(
			'-created_at',
			'-pk',
		)
		return Response(OrderSerializer(orders, many=True).data)

	def post(self, request):
		input_serializer = OrderCreateSerializer(data=request.data)
		input_serializer.is_valid(raise_exception=True)

		try:
			order = place_order(input_serializer.validated_data['items'])
		except OrderPlacementError as error:
			raise ValidationError({'items': str(error)}) from error

		return Response(
			OrderSerializer(order).data,
			status=status.HTTP_201_CREATED,
		)


class OrderDetailView(APIView):
	def get(self, request, pk):
		order = get_object_or_404(
			Order.objects.prefetch_related('items__product'),
			pk=pk,
		)
		return Response(OrderSerializer(order).data)
