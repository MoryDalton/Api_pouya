from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer, CharField, EmailField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import Users, ValidNumbers

from django_jalali.serializers.serializerfield import JDateTimeField


class CustomValidation(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "A server error occurred."

    def __init__(self, detail, field, st, status_code):
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = {"status": st, field: detail}
        else:
            self.detail = {"status": st, "detail": self.default_detail}


class UserShowSerializer(ModelSerializer):
    created_date = JDateTimeField(read_only=True)

    class Meta:
        model = Users
        fields = ("id", "phone", "is_superuser", "email", "name",
                  "family", "store", "is_active", "created_date")

        # fields = "__all__"


class CreateUserSerializer(ModelSerializer):

    # email = EmailField(required=False)
    store = CharField(required=False)
    created_date = JDateTimeField(read_only=True)

    class Meta:
        model = Users
        fields = ("id", "phone", "email", "name", "family",
                  "store", "password", "created_date")
        extra_kwargs = {"password": {"write_only": True}}

    # create user
    def create(self, validated_data):
        # check if user in valid number to active user:
        if ValidNumbers.objects.filter(phone=validated_data["phone"]).exists():
            validated_data["is_active"] = True

        password = validated_data.pop("password", None)
        # instance = self.Meta.model(**validated_data)
        instance = Users.objects.create(**validated_data)
        if password != None:
            instance.set_password(password)
        instance.save()
        return instance


class EditUserSerializer(ModelSerializer):
    created_date = JDateTimeField(read_only=True)
    update_date = JDateTimeField(read_only=True)

    class Meta:
        model = Users
        fields = ("email", "name", "family", "store",
                  "created_date", "update_date")

    def update(self, instance, validated_data):

        return super().update(instance=instance, validated_data=validated_data)


class UserChangePasswordSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Users
        fields = ("password",)

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password"])
        instance.save()
        return instance


class LogOutUserSerializer(Serializer):
    refresh = CharField(max_length=230)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, validated_data):
        # The default result (access/refresh tokens)
        try:
            user = Users.objects.get(phone=validated_data["phone"])

        except Users.DoesNotExist:
            raise CustomValidation("No active account found with the given credentials",
                                   "detail", "ERROR", status_code=status.HTTP_401_UNAUTHORIZED)

        if user.is_active:
            d = {"status": "OK"}
            data = super(CustomTokenObtainPairSerializer,
                         self).validate(validated_data)
            # find user data
            serializer = UserShowSerializer(user)
            # Custom data you want to include
            d.update({"detail": {"user": serializer.data, "data": data}})
            return d

        raise CustomValidation("No active account found with the given credentials",
                               "detail", "ERROR", status_code=status.HTTP_401_UNAUTHORIZED)


class ValidNumbersSerializer(ModelSerializer):
    created_date = JDateTimeField(read_only=True)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ValidNumbers
        fields = ("id", "phone", "name", "created_date")

    def create(self, validated_data):

        instance = ValidNumbers.objects.create(**validated_data)
        instance.save()
        user = Users.objects.filter(phone=instance.phone).first()

        if user:
            user.is_active = True
            user.save()
        return instance


class ValidNumberEditSerializer(ModelSerializer):
    class Meta:
        model = ValidNumbers
        fields = ("phone", "name")

    def update(self, instance, validated_data):
        return super().update(instance=instance, validated_data=validated_data)
