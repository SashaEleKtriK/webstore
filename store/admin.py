from django.contrib import admin
from .models import Product, ProductInOrder, Order, ProductOnStorage, OrderPoint, ProductPhoto, Brand, \
    OrderStatus, Category, SubCategory, StuffCategory

admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(ProductPhoto)
admin.site.register(OrderPoint)
admin.site.register(ProductOnStorage)
admin.site.register(Order)
admin.site.register(ProductInOrder)
admin.site.register(OrderStatus)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(StuffCategory)

