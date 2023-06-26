from django.db import models


class Products(models.Model):
    name = models.CharField(max_length=100, null=False)
    cost = models.CharField(max_length=100, null=False)

    def __str__(self) -> str:
        return self.name


#PRODUCTS MODEL:
#fileds:(name, id, code, price, is_active, min_count, description, image)