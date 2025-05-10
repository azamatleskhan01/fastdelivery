from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Restaurant, MenuItem, CartItem, Order, OrderItem, Product

# Register your models here.
admin.site.register(Restaurant)
admin.site.register(MenuItem)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Product)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('budget',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('budget',)}),
    )
