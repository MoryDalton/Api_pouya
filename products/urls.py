from django.urls import path
from products.views import (ShowProductsView, CreateProductView,
                            EditProductsView, ProductCategoryView, ProductCategoryEditView)


urlpatterns = [
    path("", ShowProductsView.as_view()),
    path("create/", CreateProductView.as_view()),
    path("category/", ProductCategoryView.as_view()),
    path("category/<int:id>/", ProductCategoryEditView.as_view()),
    path("<str:code>/", EditProductsView.as_view())
    # path("category/<int:id>/products/", CategoryShowProductsView.as_view())
]
