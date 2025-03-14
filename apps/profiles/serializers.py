from rest_framework import serializers
from .models import ShippingAddress, User


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'avatar', 'account_type')


class ShippingAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShippingAddress
        fields = (
            'id',
            'full_name',
            'email', 'phone', 'address', 'city', 'country', 'zipcode')
