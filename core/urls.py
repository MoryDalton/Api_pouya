from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# from django.contrib.auth.decorators import login_required, permission_required
# from django.views.static import serve
from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="API Documents",
        default_version='v1',
        description="Informations about API",
        #   terms_of_service="https://www.google.com/policies/terms/",
        #   contact=openapi.Contact(email="contact@snippets.local"),
        #   license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


# @login_required
# def protected_serve(request, path, document_root=None, show_indexes=False):
#     a = serve(request, path, document_root, show_indexes)

#     print(a)
#     return a


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include("users.urls")),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),

    path('', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc', schema_view.with_ui(
        'redoc', cache_timeout=0), name='schema-redoc'),
]


urlpatterns += static("static/", document_root=settings.STATIC_ROOT)
urlpatterns += static("media/", document_root=settings.MEDIA_ROOT)
# print(urlpatterns[-1].pattern)
# path(r'^%s(?P<path>.*)$' %settings.MEDIA_URL[1:], protected_serve, {'document_root': settings.MEDIA_ROOT}),
