from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from cart.models import Cart, Items
from cart.serializer import (
    CartSerializer, EditCartSerializer, CreateCartSerializer)

from drf_yasg.utils import swagger_auto_schema

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# show all carts : admin
class CartView(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        data = Cart.objects.all()
        serializer = CartSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# show one cart and delete
class ViewDeleteCardView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        user = request.user

        try:
            cart = Cart.objects.get(id=id)
            if user.is_superuser or cart.user == user:
                serializer = CartSerializer(cart)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"message": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        except:
            return Response({"message": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

    # @swagger_auto_schema(request_body=EditCartSerializer)
    # def put(self, request, id):
    #     cart = Cart.objects.get(id=id)
    #     new_data = request.data

    #     serializer = EditCartSerializer(instance=cart, data=new_data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        user = request.user
        try:
            cart = Cart.objects.get(id=id)
            if (not cart.done) and (user.is_superuser or cart.user == user):
                cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"message": "you can't delete cart that already done!"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"message": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)


# class ItemstView(APIView):

#     def get(self, request):
#         data = Items.objects.all()
#         print(data)
#         serializer = ItemSerializer(data, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


# create cart : isauth
class CreateCartView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=CreateCartSerializer)
    def post(self, request):
        data = request.data
        serializer = CreateCartSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# show all carts of user by phone: isauth
class UserCartsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, phone):
        user = request.user

        try:
            data = Cart.objects.filter(user_id=phone)

            if data and (user.is_superuser or (phone == user.phone and data)):
                serializer = CartSerializer(data, many=True)
                return Response(serializer.data)
            return Response({"message": "User not found or User doesn't have Cart"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"message": "User not found or User doesn't have Cart"}, status=status.HTTP_404_NOT_FOUND)


# done cart : admin
class CartDoneView(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request, id):
        try:
            cart = Cart.objects.get(id=id)
        except:
            return Response({"message": "Cart not found"})

        cart.done = True
        cart.save()
        return Response({"message": "Cart done!"})
