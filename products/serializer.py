import os
import shutil

from django.conf import settings

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from products.models import Products, ImageProduct, ProductCategory

from django_jalali.serializers.serializerfield import  JDateTimeField


class ImageProductSerializer(ModelSerializer):
    class Meta:
        model = ImageProduct
        fields = ("image",)
        # fields = ("id", "product", "image")


# CREATE AND SHOW PRODUCTS
class ProductSerializer(ModelSerializer):
    images = ImageProductSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(child=serializers.ImageField(
    ), required=False, write_only=True, default=["default.jpg"])
    created_date=JDateTimeField(read_only=True)
    
    class Meta:
        model = Products
        fields = ("name", "code", "price", "is_active",
                  "min_count", "desc", "category", "created_date", "images", "uploaded_images")

    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images")
        product = Products.objects.create(**validated_data)
        for image in uploaded_images:
            ImageProduct.objects.create(product=product, image=image)

        return product


# EDIT PRODUCT BY PRODUCT CODE
class EditProductSerializer(ModelSerializer):
    images = ImageProductSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(default=["default.jpg"],
                                            child=serializers.ImageField(),
                                            write_only=True, required=False)

    class Meta:
        model = Products
        fields = ("name", "price", "is_active", "min_count",
                  "desc", "category", "images", "uploaded_images")

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop("uploaded_images")

        images_path = os.path.join(settings.MEDIA_ROOT, instance.code)

        if os.path.exists(images_path):
            shutil.rmtree(images_path)
        old_images = ImageProduct.objects.filter(product_id=instance.code)
        old_images.delete()

        for image in uploaded_images:
            ImageProduct.objects.create(image=image, product=instance)

        return super().update(instance=instance, validated_data=validated_data)


# category create and show
class ProductCategorySerializer(ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ("id", "name")


class SimpleProductShowSerializer(ModelSerializer):
    class Meta:
        model = Products
        fields = ("name", "code", "price", "is_active", "min_count", "desc")


# class OneCategorySerializer(ModelSerializer):
#     products = SimpleProductShowSerializer(many=True)

#     class Meta:
#         model = ProductCategory
#         fields = ("id", "name", "products")
