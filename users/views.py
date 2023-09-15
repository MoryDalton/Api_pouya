from multiprocessing import Process

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import Users, ValidNumbers
from users.serializer import (CreateUserSerializer, LogOutUserSerializer, EditUserSerializer,
                              UserShowSerializer, UserChangePasswordSerializer, ValidNumbersSerializer,
                              ValidNumberEditSerializer)
from users.serializer import CustomTokenObtainPairSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import sms
from test_response import response_OK, response_ERROR

from rest_framework_simplejwt.tokens import RefreshToken


# create token for forget password user
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token)
    }


# show all users
class UserShowAllView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = Users.objects.all().order_by("is_active", "-update_date")
        serializer = UserShowSerializer(data, many=True)
        return Response(response_OK(serializer.data), status=status.HTTP_200_OK)


# create user
class CreateUserShow(APIView):
    permission_classes = (AllowAny, )

    # create user with sms:
    @swagger_auto_schema(request_body=CreateUserSerializer, manual_parameters=[openapi.Parameter(
        'code', openapi.IN_QUERY, description="code", type=openapi.TYPE_STRING)])
    def post(self, request):

        code = request.GET.get("code")
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():

            # if code is in parameters:
            if code:
                response = sms.check_code(
                    phone=serializer.validated_data["phone"], code=code)

                if response[0]:
                    serializer.save()
                    return Response(response_OK("User created"), status=status.HTTP_201_CREATED)
                return Response(response_ERROR(response[1]), status=status.HTTP_400_BAD_REQUEST)

            # first time call create user:
            res = sms.check_before_send(
                phone=serializer.validated_data["phone"])

            if res:
                t_send_email = Process(target=sms.send_message, args=(
                    serializer.validated_data["phone"],))
                t_send_email.start()
                return Response(response_OK("sms sent"), status=status.HTTP_200_OK)

            return Response(response_ERROR("please try after 2 minutes."), status=status.HTTP_400_BAD_REQUEST)

        return Response(response_ERROR(serializer.errors), status=status.HTTP_400_BAD_REQUEST)


# show one user
class ShowOneUserView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, phone):

        try:
            user = Users.objects.get(phone=phone)
            serializer = UserShowSerializer(user)
            return Response(response_OK(serializer.data), status=status.HTTP_200_OK)

        except:
            return Response(response_ERROR("User not found."), status=status.HTTP_404_NOT_FOUND)


# edit user info
class EditUserShow(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=EditUserSerializer)
    def put(self, request, phone):

        try:
            user = Users.objects.get(phone=phone)
        except:
            return Response(response_ERROR("User not found."), status=status.HTTP_404_NOT_FOUND)

        if request.user == user:
            serializer = EditUserSerializer(instance=user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(response_OK(serializer.data), status=status.HTTP_200_OK)
            return Response(response_ERROR(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        return Response(response_ERROR("not allowed."), status=status.HTTP_400_BAD_REQUEST)


# change password
class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=UserChangePasswordSerializer)
    def put(self, request, phone):

        try:
            user = Users.objects.get(phone=phone)
        except:
            return Response(response_ERROR("not allowed."), status=status.HTTP_400_BAD_REQUEST)

        if request.user == user:
            serializer = UserChangePasswordSerializer(
                instance=user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(response_OK("password changed."), status=status.HTTP_200_OK)
            return Response(response_ERROR(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        return Response(response_ERROR("not allowed."), status=status.HTTP_400_BAD_REQUEST)


# forget password
class UserForgetPasswordView(APIView):
    permission_classes = [AllowAny,]

    @swagger_auto_schema(manual_parameters=[openapi.Parameter('code', openapi.IN_QUERY, description="code", type=openapi.TYPE_STRING)])
    def get(self, request, phone):

        try:
            user = Users.objects.get(phone=phone, is_active=True)

            # if code in parameters:-> check code and set password:
            code = request.GET.get("code")
            if code:
                response = sms.check_code(phone=phone, code=code)
                if response[0]:

                    token = get_tokens_for_user(user)
                    return Response(response_OK(token), status=status.HTTP_200_OK)

                return Response(response_ERROR(response[1]), status=status.HTTP_400_BAD_REQUEST)

            # with no parameters:-> check for send sms:
            res = sms.check_before_send(phone=phone)
            if res:
                t_send_email = Process(target=sms.send_message, args=(phone,))
                t_send_email.start()
                return Response(response_OK("sms sent"), status=status.HTTP_200_OK)
            return Response(response_ERROR("please try after 2 minutes."), status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response(response_ERROR("User not found or not active."), status=status.HTTP_404_NOT_FOUND)


# logout users
class LogOutUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogOutUserSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.data["refresh"]
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response(response_OK("User logged out"), status=status.HTTP_200_OK)
            except Exception as e:
                return Response(response_ERROR(str(e)), status=status.HTTP_400_BAD_REQUEST)

        return Response(response_ERROR(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
# BlacklistedToken.objects.filter(token__expires_at__lt=datetime.now()).delete()


# loging view
class CustomTokenObtainPairView(TokenObtainPairView):
    # create new token to user
    serializer_class = CustomTokenObtainPairSerializer


# admin active user
class UserActiveView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, phone):

        try:
            user = Users.objects.get(phone=phone)
        except Users.DoesNotExist:
            return Response(response_ERROR("User not found"), status=status.HTTP_404_NOT_FOUND)

        user.is_active = True
        user.save()
        return Response(response_OK("User actived"), status=status.HTTP_200_OK)


# admin deactive user
class UserDeactiveView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, phone):

        try:
            user = Users.objects.get(phone=phone)
        except Users.DoesNotExist:
            return Response(response_ERROR("User not found"), status=status.HTTP_404_NOT_FOUND)

        user.is_active = False
        user.save()
        return Response(response_OK("User deactived"), status=status.HTTP_200_OK)


# show or create valid numbers : admin
class ValidNumbersView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = ValidNumbers.objects.all()
        serializer = ValidNumbersSerializer(data, many=True)
        return Response(response_OK(serializer.data), status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ValidNumbersSerializer)
    def post(self, request):
        data = request.data
        serializer = ValidNumbersSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(response_OK("phone added"), status=status.HTTP_201_CREATED)

        return Response(response_ERROR(serializer.errors), status=status.HTTP_400_BAD_REQUEST)


# edit valid number : admin
class ValidNumberEditView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, phone):
        data = request.data
        try:
            user = ValidNumbers.objects.get(phone=phone)
            serializer = ValidNumberEditSerializer(instance=user, data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(response_OK(serializer.data), status=status.HTTP_200_OK)
            return Response(response_ERROR(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response(response_ERROR("User not found"), status=status.HTTP_404_NOT_FOUND)


# delete valid number : admin
class ValidNumberDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, phone):
        try:
            number = ValidNumbers.objects.get(phone=phone)
            number.delete()
            try:
                user = Users.objects.get(phone=number.phone)
                user.is_active = False
                user.save()
            except:
                pass
            return Response(response_OK("phone deleted"), status=status.HTTP_204_NO_CONTENT)

        except:
            return Response(response_ERROR("User not found"), status=status.HTTP_404_NOT_FOUND)
