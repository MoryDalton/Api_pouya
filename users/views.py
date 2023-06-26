from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.serializer import CreateUserSerializer, LogOutUserSerializer

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from users.serializer import CustomTokenObtainPairSerializer


class CreateUserShow(APIView):
    # create new user
    # data : email, password
    permission_classes = (AllowAny, )

    def post(self, request):
        print(request.data)
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogOutUserView(APIView):
    # permission_classes = (IsAuthenticated, )

    def post(self, request):
        serializer = LogOutUserSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.data["refresh"]
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response(status=status.HTTP_205_RESET_CONTENT)
            except Exception as e:
                return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# BlacklistedToken.objects.filter(token__expires_at__lt=datetime.now()).delete()


class CustomTokenObtainPairView(TokenObtainPairView):
    # create new token to user
    serializer_class = CustomTokenObtainPairSerializer


# TODO:update user password and detail
