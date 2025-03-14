from autoslug import AutoSlugField
from django.db import models
from apps.common.models import BaseModel, IsDeletedModel
from apps.sellers.models import Seller


class Category(BaseModel):
    """
    Представляет категорию продукта.

    Атрибуты:
    name (str): Имя категории, уникальное для каждого экземпляра.
    slug (str): Слаг, сгенерированный из имени, используемый в URL-адресах.
    image (ImageField): Изображение, представляющее категорию.

    Методы:
    __str__():
    Возвращает строковое представление имени категории.
    """

    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from='name', always_update=True)
    image = models.ImageField(upload_to='category_images/')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Product(IsDeletedModel):
    """
    Поля для продукта.

    Атрибуты:
    seller (ForeignKey): Пользователь, продающий продукт.
    name (str): Название продукта.
    slug (str): Слаг, сгенерированный из названия, используемый в URL-адресах.
    desc (str): Описание продукта.
    price_old (Decimal): Первоначальная цена продукта.
    price_current (Decimal): Текущая цена продукта.
    category (ForeignKey): Категория, к которой принадлежит продукт.
    in_stock (int): Количество продукта на складе.
    image1 (ImageField): Первое изображение продукта.
    image2 (ImageField): Второе изображение продукта.
    image3 (ImageField): Третье изображение продукта.
    """

    seller = models.ForeignKey(
        Seller, on_delete=models.SET_NULL, related_name='products', null=True)
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="name", db_index=True)
    desc = models.TextField()
    price_old = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price_current = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products')
    in_stock = models.IntegerField(default=5)

    # Only 3 images are allowed
    image1 = models.ImageField(upload_to='product_images/')
    image2 = models.ImageField(upload_to='product_images/', blank=True)
    image3 = models.ImageField(upload_to='product_images/', blank=True)

    def __str__(self):
        return str(self.name)
