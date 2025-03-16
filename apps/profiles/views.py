from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsOwner
from apps.profiles.models import ShippingAddress, Order, OrderItem
from apps.profiles.serializers import (
    ProfileSerializer, ShippingAddressSerializer)
from apps.common.utils import set_dict_attr
from apps.shop.serializers import OrderSerializer, CheckItemOrderSerializer


tags = ['Profiles']


class ProfileView(APIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsOwner]

    @extend_schema(
        summary='Получение профиля',
        description="""
            Эта конечная точка позволяет пользователю получить свой профиль.
        """,
        tags=tags,
    )
    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(data=serializer.data, status=200)

    @extend_schema(
        summary='Обновление профиля',
        description="""
            Эта конечная точка позволяет юзеру редактировать свой профиль.
        """,
        tags=tags,
    )
    def put(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = set_dict_attr(user, serializer.validated_data)
        user.save()
        serializer = self.serializer_class(user)
        return Response(data=serializer.data)

    @extend_schema(
        summary='Отключение профиля',
        description="""
            Эта конечная точка позволяет пользователю отключить свой профиль.
        """,
        tags=tags,
    )
    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return Response(data={'message': 'Аккаунт пользователя деактивирован'})


class ShippingAddressesView(APIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsOwner]

    @extend_schema(
        summary='Получение адреса доставки',
        description="""
            Эта конечная точка возвращает все адреса доставки,
            связанный с юзером.
        """,
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        shipping_addresses = ShippingAddress.objects.filter(user=user)

        serializer = self.serializer_class(shipping_addresses, many=True)
        return Response(data=serializer.data)

    @extend_schema(
        summary='Создать адрес доставки.',
        description="""
            Эта конечная точка создает адрес доставки.
        """,
        tags=tags,
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        shipping_address, _ = ShippingAddress.objects.get_or_create(
            user=user, **data)
        serializer = self.serializer_class(shipping_address)
        return Response(data=serializer.data, status=201)


class ShippingAddressViewID(APIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = (IsOwner,)

    def get_object(self, user, shipping_id):
        shipping_address = ShippingAddress.objects.get_or_none(id=shipping_id)
        if shipping_address is not None:
            self.check_object_permissions(self.request, shipping_address)
        return shipping_address

    @extend_schema(
        summary='Получение адреса по ID',
        description="""
            Эта конечная точка возвращает один адрес доставки,
            связанный с юзером.
        """,
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        shipping_address = self.get_object(user, kwargs['id'])
        if not shipping_address:
            return Response(
                data={'message': 'Адрес доставки не найден!'}, status=404)
        serializer = self.serializer_class(shipping_address)
        return Response(data=serializer.data)

    @extend_schema(
        summary='Обновление адреса по ID',
        description="""
            Эта конечная точка позволяет юзеру обновить свой адрес доставки.
        """,
        tags=tags,
    )
    def put(self, request, *args, **kwargs):
        user = request.user
        shipping_address = self.get_object(user, kwargs['id'])
        if not shipping_address:
            return Response(
                data={'message': 'Адрес доставки не найден!'}, status=404)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        shipping_address = set_dict_attr(shipping_address, data)
        shipping_address.save()
        serializer = self.serializer_class(shipping_address)
        return Response(data=serializer.data, status=200)

    @extend_schema(
        summary='Удалить адрес доставки по ID',
        description="""
            Эта конечная точка позволяет юзеру удалить свой адрес доставки.
        """,
        tags=tags,
    )
    def delete(self, request, *args, **kwargs):
        user = request.user
        shipping_address = self.get_object(user, kwargs["id"])
        if not shipping_address:
            return Response(
                data={"message": 'Адрес доставки не найден!'}, status=404)
        shipping_address.delete()
        return Response(
            data={"message": 'Адрес доставки успешно удален'}, status=200)


class OrdersView(APIView):
    serializer_class = OrderSerializer
    permission_classes = (IsOwner,)

    @extend_schema(
        operation_id="orders_view",
        summary="Orders Fetch",
        description="""
            This endpoint returns all orders for a particular user.
        """,
        tags=tags
    )
    def get(self, request):
        user = request.user
        orders = (Order.objects.filter(user=user)
                  .prefetch_related("orderitems", "orderitems__product")
                  .order_by("-created_at"))
        serializer = self.serializer_class(orders, many=True)
        return Response(data=serializer.data, status=200)


class OrderItemView(APIView):
    serializer_class = CheckItemOrderSerializer
    permission_classes = (IsOwner,)

    @extend_schema(
        operation_id='orders_items_view',
        summary='Заказы на товар',
        description="""
            Эндпоинт возвращает все заказы товаров для конкретного юзера.
        """,
        tags=tags,

    )
    def get(self, request, **kwargs):
        order = Order.objects.get_or_none(tx_ref=kwargs['tx_ref'])
        if not order or order.user != request.user:
            return Response(
                data={'message': 'Заказа не существует'}, status=404)
        order_items = OrderItem.objects.filter(order=order)
        serializer = self.serializer_class(order_items, many=True)
        return Response(data=serializer.data, status=200)
