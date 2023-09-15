import os
import shutil

from django.conf import settings
from django.core.paginator import Paginator

from rest_framework import status
from django.db.models import ProtectedError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from products.serializer import ProductSerializer, EditProductSerializer, ProductCategorySerializer, SimpleProductShowSerializer
from products.models import Products, ProductCategory

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.http import HttpRequest
from test_response import response_OK, response_ERROR


def paginator_next_previous_page(request, paginator, page):
    next = ''
    previous = ''
    all_pages = paginator.num_pages
    count = paginator.count
    if 1 <= page < all_pages:
        next = HttpRequest.build_absolute_uri(request, f'?page={page+1}')
    if 1 < page <= all_pages:
        previous = HttpRequest.build_absolute_uri(request, f'?page={page-1}')

    return (count, all_pages, next, previous)


# SHOW ALL PRODUCTS
class ShowProductsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(
            'page', openapi.IN_QUERY, description="page number to view (number)", type=openapi.TYPE_STRING),
            openapi.Parameter(
            'limit', openapi.IN_QUERY, description="limit product to view (number)", type=openapi.TYPE_STRING)]
    )
    def get(self, request):
        # print(request.build_absolute_uri())
        # print(request.user.is_superuser)
        # print(request.auth)
        if request.user.is_superuser:
            data = Products.objects.all().order_by("-update_date")
        else:
            data = Products.objects.filter(
                is_active=True).order_by("-update_date")

        try:
            page_limit = int(request.GET.get("limit", "10"))
        except:
            return Response(response_ERROR("wrong type limit"), status=status.HTTP_400_BAD_REQUEST)
        my_paginator = Paginator(data, page_limit)
        try:
            page_number = int(request.GET.get("page", "1"))

            page_data = paginator_next_previous_page(request,
                                                     my_paginator, page_number)

            if 0 < page_number <= page_data[1]:
                total_data = my_paginator.get_page(page_number)

                serializer = ProductSerializer(total_data, many=True)
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


# CREATE PRODUCT
class CreateProductView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(request_body=ProductSerializer)
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(response_OK("Product created"), status=status.HTTP_201_CREATED)
        return Response(response_ERROR(serializer.errors), status=status.HTTP_400_BAD_REQUEST)


# EDIT PRODUCT
class EditProductsView(APIView):
    permission_classes = [IsAdminUser]

    # show one product with code:
    def get(self, request, code):
        try:
            product = Products.objects.get(code=code)
            serializer = EditProductSerializer(product)
            return Response(response_OK(serializer.data), status=status.HTTP_200_OK)
        except Products.DoesNotExist:
            return Response(response_ERROR("Product not found"), status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(request_body=EditProductSerializer)
    def put(self, request, code):

        try:
            product = Products.objects.get(code=code)
            data = request.data
            serializer = EditProductSerializer(instance=product, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(response_OK(serializer.data), status=status.HTTP_200_OK)
        except Products.DoesNotExist:
            return Response(response_ERROR("Product not found"), status=status.HTTP_404_NOT_FOUND)
        return Response(response_ERROR(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, code):

        try:
            product = Products.objects.get(code=code)
            product.delete()
            images_path = os.path.join(settings.MEDIA_ROOT, code)

            if os.path.exists(images_path):
                shutil.rmtree(images_path)

            return Response(response_ERROR("Product deleted"), status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(response_ERROR("Product not found"), status=status.HTTP_404_NOT_FOUND)


# category create and show:
class ProductCategoryView(APIView):
    permission_classes = [IsAuthenticated]
    # show all categories

    def get(self, request):
        category = ProductCategory.objects.all()
        serializer = ProductCategorySerializer(category, many=True)
        return Response(response_OK(serializer.data), status=status.HTTP_200_OK)

    # create a new category
    @swagger_auto_schema(request_body=ProductCategorySerializer)
    def post(self, request):
        if request.user.is_superuser:
            serializer = ProductCategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(response_OK(serializer.data), status=status.HTTP_201_CREATED)
            return Response(response_ERROR(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        return Response(response_ERROR("You do not have permission to perform this action."), status=status.HTTP_403_FORBIDDEN)


# category edit and delete:
class ProductCategoryEditView(APIView):
    permission_classes = [IsAuthenticated]

    # show one category by id
    def get(self, request, id):

        if request.user.is_superuser:
            data = Products.objects.filter(category=id)
        else:
            data = Products.objects.filter(category=id, is_active=True)

        if data:
            serializer = SimpleProductShowSerializer(data, many=True)
            return Response(response_OK(serializer.data), status=status.HTTP_200_OK)

        return Response(response_ERROR("Category not found"), status=status.HTTP_404_NOT_FOUND)

    # edit category by id

    @swagger_auto_schema(request_body=ProductCategorySerializer)
    def put(self, request, id):
        if request.user.is_superuser:
            try:
                category = ProductCategory.objects.get(id=id)
            except ProductCategory.DoesNotExist:
                return Response(response_ERROR("Category not found"), status=status.HTTP_404_NOT_FOUND)
            serializer = ProductCategorySerializer(
                instance=category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(response_OK(serializer.data), status=status.HTTP_200_OK)
            return Response(response_ERROR(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        return Response(response_ERROR("You do not have permission to perform this action."), status=status.HTTP_403_FORBIDDEN)

    # delete category by id
    def delete(self, request, id):
        if request.user.is_superuser:
            try:
                category = ProductCategory.objects.get(id=id)
                category.delete()
                return Response(response_OK("category deleted"), status=status.HTTP_204_NO_CONTENT)
            except ProductCategory.DoesNotExist:
                return Response(response_ERROR("Category not found"), status=status.HTTP_404_NOT_FOUND)
            except ProtectedError as e:
                data = [product.code for product in e.protected_objects]
                return Response(response_ERROR({"message": e.args[0], "products": data}), status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(response_ERROR("You do not have permission to perform this action."), status=status.HTTP_403_FORBIDDEN)
