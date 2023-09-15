from rest_framework import serializers
from users.models import Users
from products.models import Products
from cart.models import Cart, Items
from users.serializer import CreateUserSerializer

from django_jalali.serializers.serializerfield import JDateTimeField


class SimpleCartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ("code", "name", "price")


class ItemSerializer(serializers.ModelSerializer):
    product = SimpleCartProductSerializer(many=False)
    cost = serializers.SerializerMethodField(method_name="total")

    class Meta:
        model = Items
        fields = ("id", "product", "quantity", "cost")

    def total(self, item):
        return item.product.price * item.quantity
    
    
class CartSerializer(serializers.ModelSerializer):
    item = ItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField(method_name="total_cost")
    created_date = JDateTimeField(read_only=True)
    user = CreateUserSerializer(read_only=True)
    id = serializers.UUIDField(read_only=True)
    done = serializers.BooleanField(read_only=True)
    
    phone = serializers.CharField(write_only=True)
    items = serializers.ListField(child=serializers.DictField(), write_only=True)

    class Meta:
        model = Cart
        fields = ("id", "phone", "items", "user", "item", "done", "created_date", "total")
        # fields = "__all__"

    def total_cost(self, cart):
        items = cart.item.all()
        return sum([item.quantity * item.product.price for item in items])
    
    def validate(self, validated_date):
        phone = validated_date["phone"]
        items = validated_date["items"]
        products = []

        try:
            user = Users.objects.get(phone=phone)
        except:
            raise serializers.ValidationError("User not found")

        try:
            for item in items:
                product = Products.objects.get(code=item["product"], is_active=True)
                products.append({"product": product, "quantity": item["quantity"]})

        except KeyError:
            raise serializers.ValidationError("invalid data")

        except:
            raise serializers.ValidationError(f"Product {item['product']} not found or unavailable")

        validated_date = {
            "user": user,
            "items": products
        }

        return validated_date

    def create(self, validated_data):
        products = validated_data.pop("items")

       # create a cart for user:
        cart = Cart.objects.create(user=validated_data["user"])

        # create items for cart:
        for product in products:
            Items.objects.create(
                product=product["product"], quantity=product["quantity"], cart=cart)

        return cart
