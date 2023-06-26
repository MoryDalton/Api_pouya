from django.urls import path
from products.views import ShowProductsView, CreateProductView


urlpatterns = [
    path("show/", ShowProductsView.as_view()),
    path("create/", CreateProductView.as_view())
]
