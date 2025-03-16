from drf_spectacular.utils import OpenApiParameter, OpenApiTypes
from core import settings


PRODUCT_PARAM_EXAMPLE = [
    OpenApiParameter(
        name='max_price',
        description='Фильтр продукта по MAX цене.',
        required=False,
        type=OpenApiTypes.INT,
    ),
    OpenApiParameter(
        name='min_price',
        description='Фильтр продукта по MIN цене.',
        required=False,
        type=OpenApiTypes.INT,
    ),
    OpenApiParameter(
        name='in_stock',
        description='Фильтр продукта по наличию.',
        required=False,
        type=OpenApiTypes.INT,
    ),
    OpenApiParameter(
        name='created_at',
        description='Фильтр продукта по дате создания.',
        required=False,
        type=OpenApiTypes.DATE,
    ),
    OpenApiParameter(
        name='page',
        description='Получить определенную страницу. По умолчанию 1',
        required=False,
        type=OpenApiTypes.INT,
    ),
    OpenApiParameter(
        name='page_size',
        description=(
            'Количество элементов на странице, '
            'которые вы хотите отобразить. '
            f'По умолчанию {settings.REST_FRAMEWORK["PAGE_SIZE"]}.'
        ),
        required=False,
        type=OpenApiTypes.INT,
    )
]
