from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers

from .models import Category, MenuItem, Cart, Order, OrderItem


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "name")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "first_name", "last_name", "email")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "slug", "title")


class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    # category = CategorySerializer(read_only=True)
    class Meta:
        model = MenuItem
        fields = ["id", "title", "price", "category", "featured"]


class CartSerializer(serializers.ModelSerializer):
    menuitem_id = serializers.IntegerField(write_only=True)
    menuitem = MenuItemSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ("id", "menuitem", "menuitem_id", "quantity", "unit_price", "price")


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["order", "menuitem", "quantity", "unit_price", "price"]


class OrderSerializer(serializers.ModelSerializer):
    orderitem = OrderItemSerializer(many=True, read_only=True, source="order")

    class Meta:
        model = Order
        fields = ["id", "user", "delivery_crew", "status", "date", "total", "orderitem"]
