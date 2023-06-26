from django.db import models


class Products(models.Model):
    name = models.CharField(max_length=100, null=False)
    code=models.IntegerField()
    price=models.IntegerField()
    is_active=models.BooleanField()
    min_count=models.IntegerField()
    desc=models.TextField()
    image=models.CharField()

    def __str__(self) -> str:
        return self.name


#PRODUCTS MODEL:
#fileds:(name, id, code, price, is_active, min_count, description, image)