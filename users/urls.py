from django.urls import path
from users.views import (CreateUserShow, LogOutUserView, CustomTokenObtainPairView, EditUserShow,
                         UserShowAllView, UserChangePasswordView, ShowOneUserView, UserActiveView, UserDeactiveView,
                         ValidNumbersView, ValidNumberEditView, ValidNumberDeleteView, UserForgetPasswordView)

from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("", UserShowAllView.as_view(), name="Show_all_users"),
    path("create/", CreateUserShow.as_view(), name="create_user"),
    path("login/", CustomTokenObtainPairView.as_view(), name="login_token"),
    path("logout/", LogOutUserView.as_view(), name="logout"),
    path("edit/<str:phone>/", EditUserShow.as_view(), name="edit_user"),
    path("changepassword/<str:phone>/", UserChangePasswordView.as_view(), name="user_change_password"),
    path("forgetpassword/<str:phone>/", UserForgetPasswordView.as_view(), name="forget_password"),
    path("login/refresh/", TokenRefreshView.as_view(), name="login_refresh_token"),
    path("active/<str:phone>/", UserActiveView.as_view(), name="active_user"),
    path("deactive/<str:phone>/", UserDeactiveView.as_view(), name="deactive_user"),
    path("validnumbers/", ValidNumbersView.as_view(), name="show_and_add_valid_users"),
    path("validnumbers/edit/<str:phone>/", ValidNumberEditView.as_view(), name="edit_valid_user"),
    path("validnumbers/delete/<str:phone>/", ValidNumberDeleteView.as_view(), name="delete_valid_user"),
    path("<str:phone>/", ShowOneUserView.as_view(), name="show_one_user"),

]
