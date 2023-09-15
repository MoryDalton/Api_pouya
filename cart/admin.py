from django.contrib import admin
from cart.models import Cart, Items


class CartAdminConfig(admin.ModelAdmin):
    model = Cart

    search_fields = ('user', 'id', 'created_date', 'done')
    list_filter = ('user', 'created_date', 'done')
    ordering = ('-created_date',)
    list_display = ('user', 'id', 'created_date', 'done')


class ItemAdminConfig(admin.ModelAdmin):
    model = Cart

    search_fields = ('id', 'cart', 'product', 'quantity')
    list_filter = ('id', 'cart', 'product', 'quantity')
    list_display = ('id', 'cart', 'product', 'quantity')


admin.site.register(Cart, CartAdminConfig)
admin.site.register(Items, ItemAdminConfig)
