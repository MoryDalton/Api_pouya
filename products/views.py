import os
import shutil

from django.conf import settings
from django.core.paginator import Paginator

from rest_framework import status
from django.db.models import ProtectedError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from products.serializer import ProductSerializer, EditProductSerializer, ProductCategorySerializer
from products.models import Products, ProductCategory

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.http import HttpRequest


def paginator_next_previous_page(request, paginator, page):
    next = ''
    previous = ''
    all_pages = paginator.num_pages
    count = paginator.count
    url = HttpRequest.build_absolute_uri(request)
    if page < all_pages and page < all_pages:
        next = HttpRequest.build_absolute_uri(request, f'?page={page+1}')
    if page > 1 and page <= all_pages:
        previous = HttpRequest.build_absolute_uri(request, f'?page={page-1}')

    return count, all_pages, next, previous


# SHOW ALL PRODUCTS
class ShowProductsView(APIView):
    # permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter(
            'page', openapi.IN_QUERY, description="page number to view", type=openapi.TYPE_STRING)]
    )
    def get(self, request):
        # print(request.build_absolute_uri())
        # print(request.user)
        # print(request.auth)
        data = Products.objects.all()
        my_paginator = Paginator(data, 2)
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
                return Response(return_data, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_404_NOT_FOUND)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


# CREATE PRODUCT
class CreateProductView(APIView):
    # permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=ProductSerializer)
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# EDIT PRODUCT
class EditProductsView(APIView):
    # permission_classes = [IsAuthenticated]

    # show one product with code:
    def get(self, request, code):
        try:
            product = Products.objects.get(code=code)
            serializer = EditProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Products.DoesNotExist:
            return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(request_body=EditProductSerializer)
    def put(self, request, code):

        try:
            product = Products.objects.get(code=code)
            data = request.data
            serilizer = EditProductSerializer(instance=product, data=data)
            if serilizer.is_valid():
                serilizer.save()
                return Response(serilizer.data, status=status.HTTP_200_OK)
        except Products.DoesNotExist:
            return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serilizer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, code):

        try:
            product = Products.objects.get(code=code)
            product.delete()
            images_path = os.path.join(settings.MEDIA_ROOT, code)
            print(images_path)

            if os.path.exists(images_path):
                shutil.rmtree(images_path)

            return Response({"message": "Product deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Products.DoesNotExist:
            return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)


# category create and show:
class ProductCategoryView(APIView):

    # show all categories
    def get(self, request):
        category = ProductCategory.objects.all()
        serializer = ProductCategorySerializer(category, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # create a new category
    @swagger_auto_schema(request_body=ProductCategorySerializer)
    def post(self, request):
        serializer = ProductCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# category edit and delete:
class ProductCategoryEditView(APIView):

    # show one category bi id
    def get(self, request, id):
        try:
            category = ProductCategory.objects.get(id=id)
        except ProductCategory.DoesNotExist:
            return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductCategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # edit category by id
    @swagger_auto_schema(request_body=ProductCategorySerializer)
    def put(self, request, id):
        try:
            category = ProductCategory.objects.get(id=id)
        except ProductCategory.DoesNotExist:
            return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductCategorySerializer(
            instance=category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # delete category by id
    def delete(self, request, id):
        try:
            category = ProductCategory.objects.get(id=id)
            category.delete()
        except ProductCategory.DoesNotExist:
            return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        except ProtectedError as e:
            data = [product.code for product in e.protected_objects]
            return Response({"message": e.args[0], "products": data}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(status=status.HTTP_204_NO_CONTENT)

