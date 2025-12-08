

from rest_framework import serializers
from .models import Drinks


class DrinkSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name', 'price', 'description']
        model = Drinks