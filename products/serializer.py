from rest_framework.serializers import ModelSerializer
from products.models import Products


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Products
        fields = '__all__'
        
        
class CreateProductSerializer(ModelSerializer):
    class Meta:
        model = Products
        fileds = '__all__'
