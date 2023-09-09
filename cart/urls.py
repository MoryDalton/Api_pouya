from django.urls import path

from cart.views import (CartView, ViewDeleteCardView,
                        CreateCartView, UserCartsView, CartDoneView)  # , ItemstView


urlpatterns = [
    path("", CartView.as_view()),
    path("create/", CreateCartView.as_view()),
    path("done/<str:id>/", CartDoneView.as_view()),
    path("user/<str:phone>/", UserCartsView.as_view()),
    path("<str:id>/", ViewDeleteCardView.as_view()),


]
