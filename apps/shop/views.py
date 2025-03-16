from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg

from apps.common.paginations import CustomPagination
from apps.shop.schema_examples import PRODUCT_PARAM_EXAMPLE
from apps.reviews.models import Review
from apps.shop.filters import ProductFilter
from apps.sellers.models import Seller
from apps.shop.models import Category, Product
from apps.profiles.models import OrderItem, ShippingAddress, Order
from apps.shop.serializers import (
    CategorySerializer,
    ProductSerializer,
    OrderItemSerializer,
    ToggleCartItemSerializer,
    CheckoutSerializer, OrderSerializer)

tags = ['Shop']


class CategoriesView(APIView):
    serializer_class = CategorySerializer

    @extend_schema(
        summary='Категории',
        description="""
            Эндпоинт для получения категорий.
        """,
        tags=tags
    )
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serializer = self.serializer_class(categories, many=True)
        return Response(data=serializer.data, status=200)

    @extend_schema(
        summary='Создание категории',
        description="""
            Эндпоинт для создания категории.
        """,
        tags=tags
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            new_cat = Category.objects.create(**serializer.validated_data)
            serializer = self.serializer_class(new_cat)
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)


class ProductsByCategoryView(APIView):
    serializer_class = ProductSerializer

    @extend_schema(
        operation_id="category_products",
        summary='Категория продукта',
        description="""
            Эндпоинт возвращает все категории.
        """,
        tags=tags
    )
    def get(self, request, *args, **kwargs):
        category = Category.objects.get_or_none(slug=kwargs['slug'])
        if not category:
            return Response(
                data={'message': 'Категории не существует!'}, status=404)
        products = Product.objects.select_related(
            'category', 'seller', 'seller__user').filter(category=category)
        serializer = self.serializer_class(products, many=True)
        return Response(data=serializer.data, status=200)


class ProductsView(APIView):
    serializer_class = ProductSerializer
    pagination_class = CustomPagination

    @extend_schema(
        operation_id='all_products',
        summary='Все продукты магазина',
        description="""
            Эндпоинт возвращает все продукты магазина.
        """,
        tags=tags,
        parameters=PRODUCT_PARAM_EXAMPLE,
    )
    def get(self, request, *args, **kwargs):
        products = Product.objects.select_related(
            'category', 'seller', 'seller__user').all()
        filterset = ProductFilter(request.GET, queryset=products)
        if filterset.is_valid():
            queryset = filterset.qs
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            serializer = self.serializer_class(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            return Response(filterset.errors, status=400)


class ProductsBySellerView(APIView):
    serializer_class = ProductSerializer

    @extend_schema(
        summary='Товары продавца по слаг',
        description="""
            Эндпоинт возвращает товары продавца по слаг.
        """,
        tags=tags
    )
    def get(self, request, *args, **kwargs):
        seller = Seller.objects.get_or_none(slug=kwargs['slug'])
        if not seller:
            return Response(
                data={'message': 'Продавец не существует!'}, status=404)
        products = Product.objects.select_related(
            'category', 'seller', 'seller__user').filter(seller=seller)
        serializer = self.serializer_class(products, many=True)
        return Response(data=serializer.data, status=200)


class ProductView(APIView):
    serializer_class = ProductSerializer

    def get_object(self, slug):
        product = Product.objects.get_or_none(slug=slug)
        return product

    @extend_schema(
        operation_id="product_detail",
        summary='Инфо о продукте.',
        description="""
            Эта конечная точка возвращает сведения о продукте через слаг.
        """,
        tags=tags
    )
    def get(self, request, *args, **kwargs):
        product = self.get_object(kwargs['slug'])
        if not product:
            return Response(data={'message': 'Продукт не найден!'}, status=404)
        avg_rating = Review.objects.filter(
            product=product).aggregate(Avg('rating'))['rating__avg']
        serializer = self.serializer_class(product)
        response_data = serializer.data
        response_data['average_rating'] = avg_rating or 0
        return Response(data=serializer.data, status=200)


class CartView(APIView):
    serializer_class = OrderItemSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary='Товары в корзине',
        description="""
            Эта конечная точка возвращает все товары в корзине пользователя.
        """,
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        orderitems = OrderItem.objects.filter(
            user=user, order=None).select_related(
                'product', 'product__seller', 'product__seller__user')
        serializer = self.serializer_class(orderitems, many=True)
        return Response(data=serializer.data)

    @extend_schema(
        summary='Действия с корзиной.',
        description="""
        Эта конечная точка позволяет пользователю или гостю
        добавлять/обновлять/удалять товар в корзине.
        Если количество равно 0, товар удаляется из корзины
        """,
        tags=tags,
        request=ToggleCartItemSerializer,
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = ToggleCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        quantity = data['quantity']

        product = Product.objects.select_related(
            'seller', 'seller__user').get_or_none(slug=data['slug'])
        if not product:
            return Response(
                {'message': 'Нет продукта с таким слаг'}, status=404)
        orderitem, created = OrderItem.objects.update_or_create(
            user=user,
            order_id=None,
            product=product,
            defaults={'quantity': quantity},
        )
        resp_message_substring = 'Обновлено в'
        status_code = 200
        if created:
            status_code = 201
            resp_message_substring = 'Добавлено в'
        if orderitem.quantity == 0:
            resp_message_substring = 'Удалено из'
            orderitem.delete()
            data = None
        if resp_message_substring != 'Удалено из':
            orderitem.product = product
            serializer = self.serializer_class(orderitem)
            data = serializer.data
        return Response(
            data={"message": f'Товар {resp_message_substring} Корзина',
                  'item': data}, status=status_code)


class CheckoutView(APIView):
    serializer_class = CheckoutSerializer
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary='Проверка',
        description="""
               Эта конечная точка позволяет пользователю создать заказ,
               через который затем может быть произведена оплата.
               """,
        tags=tags,
        request=CheckoutSerializer,
    )
    def post(self, request, *args, **kwargs):
        # Proceed to checkout
        user = request.user
        orderitems = OrderItem.objects.filter(user=user, order=None)
        if not orderitems.exists():
            return Response({"message": "No Items in Cart"}, status=404)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        shipping_id = data.get("shipping_id")
        if shipping_id:
            # Получаем информацию о доставке на основе идентификатора доставки.
            shipping = ShippingAddress.objects.get_or_none(id=shipping_id)
            if not shipping:
                return Response(
                    {'message': 'Нет адреса доставки с таким ID'}, status=404)

        def append_shipping_details(shipping):
            fields_to_update = [
                'full_name',
                'email',
                'phone',
                'address',
                'city',
                'country',
                'zipcode',
            ]
            data = {}
            for field in fields_to_update:
                value = getattr(shipping, field)
                data[field] = value
            return data

        order = Order.objects.create(
            user=user, **append_shipping_details(shipping))
        orderitems.update(order=order)

        serializer = OrderSerializer(order)
        return Response(
            data={'message': 'Заказ успешно оформлен!',
                  "item": serializer.data}, status=200)
