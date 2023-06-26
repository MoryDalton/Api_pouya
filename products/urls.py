from django.urls import path
from products.views import ShowProductsView, CreateProductView, EditProductsView


urlpatterns = [
    path("show/", ShowProductsView.as_view()),
    path("create/", CreateProductView.as_view()),
    path("edit/<string:code>", EditProductsView.as_view())
]
