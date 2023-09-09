import os

from django.db import models

from django_jalali.db import models as jmodels


class ProductCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False)
    created_date = jmodels.jDateTimeField(auto_now_add=True)
    update_date = jmodels.jDateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Category"

    def __str__(self) -> str:
        return self.name


class Products(models.Model):
    name = models.CharField(max_length=100, null=False)
    code = models.CharField(primary_key=True, max_length=100, null=False, unique=True)
    price = models.IntegerField(null=False)
    is_active = models.BooleanField(null=False)
    min_count = models.IntegerField(null=False)
    desc = models.TextField(null=False)
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, related_name="products")
    created_date = jmodels.jDateTimeField(auto_now_add=True)
    update_date = jmodels.jDateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Products"
        verbose_name_plural = "Products"

    def __str__(self) -> str:
        return f"{self.name}:{self.code}"


def upload_to(instance, filename):

    image_path = os.path.join(instance.product.code, filename)
    # image_path = "static/sample/test/img.jpg"
    # print(image_path)
    return image_path


class ImageProduct(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=upload_to, null=True, blank=True)
    created_date = jmodels.jDateTimeField(auto_now_add=True)
    update_date = jmodels.jDateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Images"
        verbose_name_plural = "Images"
