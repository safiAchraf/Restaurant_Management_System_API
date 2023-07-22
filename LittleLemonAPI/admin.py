from django.contrib import admin
from .models import Cart, MenuItem, Category, Order, OrderItem

admin.site.site_header = "Little Lemon Admin"
admin.site.register(Cart)
admin.site.register(MenuItem)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
