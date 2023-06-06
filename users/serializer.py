from rest_framework.serializers import ModelSerializer, Serializer, CharField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.models import Users


class CreateUserSerializer(ModelSerializer):

    class Meta:
        model = Users
        fields = ("email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password != None:
            instance.set_password(password)
        instance.save()
        return instance


class LogOutUserSerializer(Serializer):
    refresh = CharField(max_length=230)


# from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        d = {'status': 'ok'}
        # The default result (access/refresh tokens)
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        # Custom data you want to include
        d.update({'data': data})
        print(attrs)
        # and everything else you want to send in the response
        return d
