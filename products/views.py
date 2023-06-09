from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from products.serializer import ProductSerializer
from products.models import Products


class ShowProductsView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        # print(request.user)
        # print(request.auth)
        data = Products.objects.all()
        serializer = ProductSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateProductView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EditProductsView(APIView):
    # permission_classes = [IsAuthenticated]

    def put(self, request, code):

        try:
            product = Products.objects.get(code=code)
            data = request.data
            serilizer = ProductSerializer(instance=product, data=data)
            if serilizer.is_valid():
                serilizer.save()
                return Response(serilizer.data, status=status.HTTP_200_OK)
        except Products.DoesNotExist:
            return Response({"message": "products not found"})
        return Response(serilizer.errors, status=status.HTTP_400_BAD_REQUEST)
