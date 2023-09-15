from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from cart.models import Cart
from cart.serializer import CartSerializer

from drf_yasg.utils import swagger_auto_schema
from test_response import response_OK, response_ERROR

# show all carts : admin
class CartView(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request):
        data = Cart.objects.all()
        serializer = CartSerializer(data, many=True)
        return Response(response_OK(serializer.data), status=status.HTTP_200_OK)


# show one cart and delete
class ViewDeleteCardView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id):
        user = request.user

        try:
            cart = Cart.objects.get(id=id)
            if user.is_superuser or cart.user == user:
                serializer = CartSerializer(cart)
                return Response(response_OK(serializer.data), status=status.HTTP_200_OK)
            return Response(response_ERROR("You do not have permission to perform this action."), status=status.HTTP_403_FORBIDDEN)
        except:
            return Response(response_ERROR("Cart not found"), status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        user = request.user
        try:
            cart = Cart.objects.get(id=id)
            if (not cart.done) and (user.is_superuser or cart.user == user):
                cart.delete()
                return Response(response_OK("Cart deleted"), status=status.HTTP_204_NO_CONTENT)
            return Response(response_ERROR("you can't delete Cart that already done!"), status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(response_ERROR("Cart not found"), status=status.HTTP_404_NOT_FOUND)


#TODO: after create cart it must return total cost:
# create cart : isauth
class CreateCartView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=CartSerializer)
    def post(self, request):
        data = request.data
        serializer = CartSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(response_OK(serializer.data), status=status.HTTP_201_CREATED)
        return Response(response_ERROR(serializer.errors), status=status.HTTP_400_BAD_REQUEST)


# show all carts of user by phone: isauth
class UserCartsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, phone):
        user = request.user

        try:
            data = Cart.objects.filter(user_id=phone)

            if data and (user.is_superuser or (phone == user.phone and data)):
                serializer = CartSerializer(data, many=True)
                return Response(response_OK(serializer.data), status=status.HTTP_200_OK)
            return Response(response_ERROR("User not found or User doesn't have Cart"), status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(response_ERROR("User not found or User doesn't have Cart"), status=status.HTTP_404_NOT_FOUND)


# done cart : admin
class CartDoneView(APIView):
    permission_classes = (IsAdminUser,)

    def get(self, request, id):
        try:
            cart = Cart.objects.get(id=id)
        except:
            return Response(response_ERROR("Cart not found"), status=status.HTTP_404_NOT_FOUND)

        cart.done = True
        cart.save()
        return Response(response_OK("Cart done"), status=status.HTTP_200_OK)
