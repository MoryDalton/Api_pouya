from rest_framework import serializers
from users.models import Users
from products.models import Products
from cart.models import Cart, Items
from products.serializer import ProductSerializer
from users.serializer import CreateUserSerializer

from django_jalali.serializers.serializerfield import JDateTimeField


class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ("code", "name", "price")


class ItemSerializer(serializers.ModelSerializer):
    product = CartProductSerializer(many=False)
    cost = serializers.SerializerMethodField(method_name="total")

    class Meta:
        model = Items
        fields = ("id", "product", "quantity", "cost")

    def total(self, item):
        return item.product.price * item.quantity


class CartSerializer(serializers.ModelSerializer):
    item = ItemSerializer(many=True)
    total = serializers.SerializerMethodField(method_name="total_cost")
    created_date = JDateTimeField(read_only=True)
    user = CreateUserSerializer()

    class Meta:
        model = Cart
        fields = ("id", "user", "item", "done", "created_date", "total")
        # fields = "__all__"

    def total_cost(self, cart):
        items = cart.item.all()
        return sum([item.quantity * item.product.price for item in items])


class CreateCartSerializer(serializers.ModelSerializer):
    items = serializers.ListField(child=serializers.DictField(
    ), write_only=True)
    user_id = serializers.CharField(write_only=True)
    item = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ("user_id", "items", "item")

    def validate(self, validated_date):
        user_id = validated_date["user_id"]
        items = validated_date["items"]
        products = []

        try:
            user = Users.objects.get(phone=user_id)
        except:
            raise serializers.ValidationError({"message": "User not found"})

        try:
            for item in items:
                product = Products.objects.get(code=item["product"], is_active=True)
                products.append({"product": product, "quantity": item["quantity"]})

        except KeyError:
            raise serializers.ValidationError({"message": "invalid data"})

        except:
            raise serializers.ValidationError(
                {f"{item['product']}": "Product not found or unavailable"})

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


class EditCartSerializer(serializers.ModelSerializer):

    items = serializers.ListField(child=serializers.DictField(
    ), write_only=True)
    # user_id = serializers.CharField(write_only=True)
    item = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ("items", "item")

    def validate(self, validated_date):
        items = validated_date["items"]
        products = []

        for item in items:
            try:
                products.append({"product": Products.objects.get(
                    code=item["product"]), "quantity": item["quantity"]})
            except:
                raise serializers.ValidationError(
                    {"message": f"Product {item['product']} not found"})

        validated_date = {
            "items": products
        }

        return validated_date

    def update(self, instance, validated_data):
        items = instance.item.all()

        items.delete()
        products = validated_data["items"]
        for product in products:
            Items.objects.create(
                product=product["product"], quantity=product["quantity"], cart=instance)

        return super().update(instance=instance, validated_data=validated_data)
