from multiprocessing import Process

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import Users, ValidNumbers, EmailVerify
from users.serializer import (CreateUserSerializer, LogOutUserSerializer, EditUserSerializer,
                              UserShowSerializer, UserChangePasswordSerializer, ValidNumbersSerializer,
                              ValidNumberEditSerializer)
from users.serializer import CustomTokenObtainPairSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import email_verify

from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token)
    }


# show all users
class UserShowAllView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = Users.objects.all().order_by("is_active", "-update_date")
        serializer = UserShowSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# create user
class CreateUserShow(APIView):
    # create new user
    # data : phone, password
    permission_classes = (AllowAny, )

    # create user without sms:
    # @swagger_auto_schema(request_body=CreateUserSerializer)
    # def post(self, request):
    #     data = request.data
    #     serializer = CreateUserSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # create user with sms:
    # @swagger_auto_schema(request_body=CreateUserSerializer, manual_parameters=[openapi.Parameter(
    #     'code', openapi.IN_QUERY, description="sms code", type=openapi.TYPE_STRING)])
    # def post(self, request):

    #     try:
    #         phone = request.data["phone"]
    #     except:
    #         return Response({"phone": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

    #     if Users.objects.filter(phone=phone):
    #         # user already exsist
    #         return Response({"phone": ["Users with this phone already exists."]}, status=status.HTTP_400_BAD_REQUEST)

    #     code = request.GET.get("code")
    #     if code:
    #         # check code sms
    #         response = sms.check_sms(phone, code)
    #         # print(response)
    #         if response[0]:
    #             # create new user
    #             serializer = CreateUserSerializer(data=request.data)
    #             if serializer.is_valid():
    #                 serializer.save()
    #                 return Response(serializer.data, status=status.HTTP_201_CREATED)
    #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #         return Response({"message": response[1]}, status=status.HTTP_400_BAD_REQUEST)

    #     print("no code")
    #     return Response(sms.send_sms(phone), status=status.HTTP_200_OK)

# -----------------------------------------------------------------------------------------------------------

    # create user with email:
    # @swagger_auto_schema(request_body=CreateUserSerializer, manual_parameters=[openapi.Parameter(
    #     'code', openapi.IN_QUERY, description="email code", type=openapi.TYPE_STRING)])
    # def post(self, request):

    #     try:
    #         email = request.data["email"]
    #     except:
    #         return Response({"email": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)

    #     if Users.objects.filter(email=email):
    #         # user already exsist
    #         return Response({"email": ["Users with this email already exists."]}, status=status.HTTP_400_BAD_REQUEST)

    #     code = request.GET.get("code")
    #     if code:
    #         # check code email
    #         response = email_verify.check_code(email, code)
    #         # print(response)
    #         if response[0]:
    #             # create new user
    #             serializer = CreateUserSerializer(data=request.data)
    #             if serializer.is_valid():
    #                 serializer.save()
    #                 return Response(serializer.data, status=status.HTTP_201_CREATED)
    #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #         return Response({"message": response[1]}, status=status.HTTP_400_BAD_REQUEST)

    # #     print("no code")
    #     t_send_email = Thread(target=email_verify.send_email, args=(email,))
    #     t_send_email.start()
    #     return Response({"message": "email sent"}, status=status.HTTP_200_OK)

# ----------------------------------------------------------------------------------------------------------------------------------------

    # create user with email BUT, first check serializer:
    @swagger_auto_schema(request_body=CreateUserSerializer, manual_parameters=[openapi.Parameter(
        'code', openapi.IN_QUERY, description="email code", type=openapi.TYPE_STRING)])
    def post(self, request):

        code = request.GET.get("code")
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():

            # if code is in parameters:
            if code:
                response = email_verify.check_code(
                    serializer.validated_data["email"], code)

                if response[0]:
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response({"message": response[1]}, status=status.HTTP_400_BAD_REQUEST)

            # first time call create user:
            res = email_verify.check_before_send(
                email=serializer.validated_data["email"])

            if res:
                t_send_email = Process(target=email_verify.send_email, args=(
                    serializer.validated_data["email"],))
                t_send_email.start()
                return Response({"message": "email sent"}, status=status.HTTP_200_OK)

            return Response({"message": "please try after 2 minutes."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# show one user
class ShowOneUserView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, phone):

        try:
            user = Users.objects.get(phone=phone)
            serializer = UserShowSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)


# edit user info
class EditUserShow(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=EditUserSerializer)
    def put(self, request, phone):

        try:
            user = Users.objects.get(phone=phone)
        except:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user == user:
            serializer = EditUserSerializer(instance=user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "not allowed."}, status=status.HTTP_400_BAD_REQUEST)

    # def delete(self, request, phone):
    #     pass


# change password
class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=UserChangePasswordSerializer)
    def put(self, request, phone):

        try:
            user = Users.objects.get(phone=phone)
        except:
            return Response({"message": "not allowed."}, status=status.HTTP_400_BAD_REQUEST)
            # return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user == user:
            serializer = UserChangePasswordSerializer(
                instance=user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "password changed."}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "not allowed."}, status=status.HTTP_400_BAD_REQUEST)


# TODO: fix this part!
class UserForgetPasswordView(APIView):
    permission_classes = [AllowAny,]

    @swagger_auto_schema(manual_parameters=[openapi.Parameter('code', openapi.IN_QUERY, description="email code", type=openapi.TYPE_STRING)])
    def get(self, request, email):
        # data={"phone": "09xxxxxxxxx"}

        try:
            user = Users.objects.get(email=email, is_active=True)
            # TODO:check validation by sms
            # if code in parameters:-> check code and set password:
            code = request.GET.get("code")
            if code:
                response = email_verify.check_code(email=email, code=code)
                if response[0]:
                    # serializer = UserChangePasswordSerializer(instance=user, data=request.data)

                    # if serializer.is_valid():
                    #     # set password:
                    #     serializer.save()
                    #     return Response({"message": "password changed."}, status=status.HTTP_200_OK)
                    # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                    token = get_tokens_for_user(user)
                    return Response(token, status=status.HTTP_200_OK)

                return Response({"message": response[1]}, status=status.HTTP_400_BAD_REQUEST)

            # with no parameters:-> check for send sms:
            res = email_verify.check_before_send(email=email)
            if res:
                t_send_email = Process(
                    target=email_verify.send_email, args=(email,))
                t_send_email.start()
                return Response({"message": "email sent"}, status=status.HTTP_200_OK)
            return Response({"message": "please try after 2 minutes."}, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # serializer = ForgetPasswordSerializser(data=request.data)
        # print(serializer)
        # if serializer.is_valid():
            # print("first ok")
            # token_serializer = CustomTokenObtainPairSerializer(serializer.data)
            # print(token_serializer)
            # print(token_serializer.data)
            # return Response(token_serializer.data, status=status.HTTP_200_OK)
            # pass


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
                return Response(status=status.HTTP_205_RESET_CONTENT)
            except Exception as e:
                return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            return Response({"message": "user not found"})

        user.is_active = True
        user.save()
        return Response({"message": "user actived!"})


# admin deactive user
class UserDeactiveView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, phone):

        try:
            user = Users.objects.get(phone=phone)
        except Users.DoesNotExist:
            return Response({"message": "user not found"})

        user.is_active = False
        user.save()
        return Response({"message": "user deactived!"})


# show or create valid numbers : admin
class ValidNumbersView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = ValidNumbers.objects.all()
        serializer = ValidNumbersSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ValidNumbersSerializer)
    def post(self, request):
        data = request.data
        serializer = ValidNumbersSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({"message": "user not found"})


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
            return Response(status=status.HTTP_204_NO_CONTENT)

        except:
            return Response({"message": "user not found"})


# TODO:update user password and detail

# TODO:
# class UserLoginSms
