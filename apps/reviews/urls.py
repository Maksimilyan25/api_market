from django.urls import path, include
from rest_framework import routers

from .views import ReviewView


router = routers.DefaultRouter()
router.register(r'', ReviewView)

urlpatterns = [
    path('', include(router.urls))
]

