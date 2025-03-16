from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from .models import Review
from .serializers import ReviewSerializer
from apps.shop.models import Product


class ReviewView(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'pk'

    def get_queryset(self):
        product_slug = self.kwargs.get('slug')
        if product_slug:
            product = Product.objects.filter(slug=product_slug).first()
            if not product:
                raise NotFound('Продукт не найден!')
            return Review.objects.filter(product=product)
        return Review.objects.all()

    def create(self, request, *args, **kwargs):
        product_slug = self.kwargs.get('slug')
        product = Product.objects.filter(slug=product_slug).first()
        if not product:
            return Response(
                {'message': 'Продукт не найден!'},
                status=status.HTTP_404_NOT_FOUND)

        if Review.objects.filter(product=product, user=request.user).exists():
            raise ValidationError('Вы уже оставили отзыв на этот продукт.')

        return super().create(request, *args, **kwargs)
