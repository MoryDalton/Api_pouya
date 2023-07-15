from django.contrib import admin
from products.models import Products, ImageProduct, ProductCategory


class ProductsAdminConfig(admin.ModelAdmin):
    model = Products

    search_fields = ('name', 'code')
    list_filter = ('is_active', 'category', 'created_date', 'update_date')
    ordering = ('-created_date', '-name', '-price')
    list_display = ('name', 'code', 'price', 'is_active',
                    'min_count', 'category', 'created_date', 'update_date')


class ProductsCategoryAdminConfig(admin.ModelAdmin):
    model = Products

    search_fields = ('id', 'name', 'created_date', 'update_date')
    list_filter = ('id', 'name', 'created_date', 'update_date')
    ordering = ('-created_date', '-name', '-update_date')
    list_display = ('id', 'name', 'created_date', 'update_date')


class ProductsImageAdminConfig(admin.ModelAdmin):
    model = Products

    search_fields = ('product', 'image', 'created_date', 'update_date')
    list_filter = ('product', 'created_date', 'update_date')
    ordering = ('-product', '-created_date', '-update_date')
    list_display = ('product', 'image', 'created_date', 'update_date')


admin.site.register(Products, ProductsAdminConfig)
admin.site.register(ImageProduct, ProductsImageAdminConfig)
admin.site.register(ProductCategory, ProductsCategoryAdminConfig)
