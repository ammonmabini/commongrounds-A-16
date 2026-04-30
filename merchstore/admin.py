from django.contrib import admin

from .models import Product, ProductType, Transaction


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type', 'owner', 'price', 'stock', 'status')
    search_fields = ('name', 'description', 'owner__display_name')
    list_filter = ('product_type', 'status')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'buyer', 'amount', 'status', 'created_on')
    list_filter = ('status', 'created_on')
    search_fields = ('product__name', 'buyer__display_name')
