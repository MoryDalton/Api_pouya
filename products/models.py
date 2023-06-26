from django.db import models


class Products(models.Model):
    name = models.CharField(max_length=100, null=False)
    code = models.CharField(max_length=100, null=False, unique=True)
    price = models.IntegerField(null=False)
    is_active = models.BooleanField(null=False)
    min_count = models.IntegerField(null=False)
    desc = models.TextField(null=False)
    image = models.CharField(max_length=100, null=False)

    def __str__(self) -> str:
        return self.name


# PRODUCTS MODEL:
# fileds:(name, id, code, price, is_active, min_count, description, image)
