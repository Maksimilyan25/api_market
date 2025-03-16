from django.db import models

from apps.common.models import IsDeletedModel
from apps.accounts.models import User
from apps.shop.models import Product


RATING_CHOICES = (
    (1, 'Плохо'),
    (2, 'Ниже среднего'),
    (3, 'Средний'),
    (4, 'Хорошо'),
    (5, 'Отлично')
)


class Review(IsDeletedModel):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='review_user')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='review_prod')
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    text = models.CharField(max_length=5000)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return self.text
