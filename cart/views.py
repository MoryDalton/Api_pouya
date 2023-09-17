from django.core.paginator import Paginator

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from cart.models import Cart
from cart.serializer import CartSerializer, ItemSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from tools import response_OK, response_ERROR, paginator_next_previous_page


# show all carts : admin
class CartView(APIView):
    permission_classes = (IsAdminUser,)

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(
            'page', openapi.IN_QUERY, description="page number to view (number)", type=openapi.TYPE_STRING),
            openapi.Parameter(
            'limit', openapi.IN_QUERY, description="limit product to view (number)", type=openapi.TYPE_STRING)]
    )
    def get(self, request):
        carts = Cart.objects.all().order_by("-created_date")

        try:
            page_limit = int(request.GET.get("limit", "10"))
        except:
            return Response(response_ERROR("wrong type limit"), status=status.HTTP_400_BAD_REQUEST)

        my_paginator = Paginator(carts, page_limit)
        try:
            page_number = int(request.GET.get("page", "1"))

            page_data = paginator_next_previous_page(
                request, my_paginator, page_number)

            if 0 < page_number <= page_data[1]:
                total_data = my_paginator.get_page(page_number)

                serializer = CartSerializer(total_data, many=True)
                return_data = {
                    "count": page_data[0],
                    "pages": page_data[1],
                    "next_page": page_data[2],
                    "previous_page": page_data[3],
                    "result": serializer.data
                }
                return Response(response_OK(return_data), status=status.HTTP_200_OK)
            return Response(response_ERROR("not found"), status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(response_ERROR("not found"), status=status.HTTP_404_NOT_FOUND)


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


# create cart : isauth
class CreateCartView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'phone': openapi.Schema(type=openapi.TYPE_STRING),
            'items': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(

                type=openapi.TYPE_OBJECT, properties={
                    'product': openapi.Schema(type=openapi.TYPE_STRING),
                    'quantity': openapi.Schema(type=openapi.TYPE_INTEGER)
                }))}))
    def post(self, request):
        data = request.data
        serializer = CartSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(response_OK(serializer.data), status=status.HTTP_201_CREATED)
        return Response(response_ERROR([f"[{key}]: {value[0]}" for key, value in serializer.errors.items()]), status=status.HTTP_400_BAD_REQUEST)


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
