from django.contrib import admin
from . models import Cart, Category, Product, CartProduct, Order

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartProduct)
admin.site.register(Order)