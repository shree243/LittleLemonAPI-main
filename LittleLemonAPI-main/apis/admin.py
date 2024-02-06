from django.contrib import admin

from .models import Category, MenuItem, Cart, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["slug", "title"]
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(MenuItem)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["user", "menuitem", "quantity", "unit_price", "price"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["user", "delivery_crew", "status", "total", "date"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "menuitem", "quantity", "unit_price", "price"]
