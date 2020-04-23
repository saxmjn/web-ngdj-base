from rest_framework import serializers
# PROJECT
from . import models


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.File
        exclude = []


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        exclude = []


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.City
        exclude = []
