from django.urls import path
from users.views import CreateUserShow, LogOutUserView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("create/", CreateUserShow.as_view(), name="create_user"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login_token"),
    path("login/refresh/", TokenRefreshView.as_view(), name="login_refresh_token"),
    path("logout/", LogOutUserView.as_view(), name="logout")
]
