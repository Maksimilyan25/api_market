from django.urls import path, include

from apps.shop.views import (
    CategoriesView,
    ProductView,
    ProductsView,
    ProductsByCategoryView,
    ProductsBySellerView, CartView, CheckoutView)
from apps.reviews.views import ReviewView
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'products/<slug:slug>', ReviewView)


urlpatterns = [
    path("categories/", CategoriesView.as_view()),
    path("categories/<slug:slug>/", ProductsByCategoryView.as_view()),
    path("sellers/<slug:slug>/", ProductsBySellerView.as_view()),
    path("products/", ProductsView.as_view()),
    path("products/<slug:slug>/", ProductView.as_view()),
    path('', include(router.urls)),
    path('cart/', CartView.as_view()),
    path('checkout/', CheckoutView.as_view()),
]
