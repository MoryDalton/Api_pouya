import uuid

from django.db import models
from users.models import Users
from products.models import Products

from django_jalali.db import models as jmodels


# cart model
class Cart(models.Model):
    user = models.ForeignKey(Users, to_field="phone",on_delete=models.CASCADE, related_name="cart")
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True)
    created_date = jmodels.jDateTimeField(auto_now_add=True)
    done = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Carts"
        verbose_name_plural = "Carts"

    def __str__(self) -> str:
        return f'{self.user.phone}: {self.id}'


# items in cart model
class Items(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="item")
    product = models.ForeignKey(Products, on_delete=models.PROTECT, related_name="product")
    quantity = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Items"
        verbose_name_plural = "Items"

    def __str__(self) -> str:
        return f'{self.cart.user.phone}'
