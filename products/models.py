from django.db import models


class Products(models.Model):
    name = models.CharField(max_length=100, null=False)
    code = models.CharField(max_length=100, null=False, unique=True)
    price = models.IntegerField(null=True)
    is_active = models.BooleanField(null=True)
    min_count = models.IntegerField(null=True)
    desc = models.TextField(null=True)
    image = models.CharField(max_length=100, null=True)

    def __str__(self) -> str:
        return self.name


# PRODUCTS MODEL:
# fileds:(name, id, code, price, is_active, min_count, description, image)
