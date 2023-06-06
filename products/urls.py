from django.urls import path
from products.views import ShowProductsView


urlpatterns = [
    path("show/", ShowProductsView.as_view())
]
