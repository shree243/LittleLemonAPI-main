from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404

from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import Category, MenuItem, Cart, Order, OrderItem
from .permissions import IsManager, IsDeliveryCrew
from .serializers import (
    GroupSerializer,
    CategorySerializer,
    MenuItemSerializer,
    UserSerializer,
    CartSerializer,
    OrderSerializer,
    OrderItemSerializer,
)


class GroupView(generics.ListAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAdminUser | IsManager]
    serializer_class = GroupSerializer


class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    ordering_fields = ["price"]
    search_fields = ["category__title"]
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [IsAdminUser | IsManager]
        return super(MenuItemsView, self).get_permissions()


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if (
            self.request.method == "POST"
            or self.request.method == "PUT"
            or self.request.method == "DELETE"
        ):
            self.permission_classes = [IsManager]
        return super(SingleMenuItemView, self).get_permissions()


class ManagerGroupViewSet(viewsets.ViewSet):
    """
    Returns all users, assign and delete user from/to 'Manager' group
    """

    permission_classes = [IsAdminUser | IsManager]

    def list(self, request):
        users = User.objects.filter(groups__name="Manager")
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def create(self, request):
        username = request.data.get("username")
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Manager")
        managers.user_set.add(user)
        return Response(
            {"message": "user added to the 'Manager' group"},
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request):
        username = request.data.get("username")
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Manager")
        managers.user_set.remove(user)
        return Response({"message": "user removed to the 'Manager' group"})


class DeliveryCrewGroupViewSet(viewsets.ViewSet):
    """
    Returns all users, assign and delete user from/to 'Delivery Crew' group
    """

    permission_classes = [IsAdminUser | IsManager]

    def list(self, request):
        users = User.objects.filter(groups__name="Delivery Crew")
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def create(self, request):
        username = request.data.get("username")
        user = get_object_or_404(User, username=username)
        delivery_crews = Group.objects.get(name="Delivery Crew")
        delivery_crews.user_set.add(user)
        return Response(
            {"message": "user added to the 'Delivery Crew' group"},
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request):
        username = request.data.get("username")
        user = get_object_or_404(User, username=username)
        delivery_crews = Group.objects.get(name="Delivery Crew")
        delivery_crews.user_set.remove(user)
        return Response({"message": "user removed to the 'Delivery Crew' group"})


class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [IsAdminUser | IsManager]
        return super(CategoryView, self).get_permissions()


class CartMenuItemView(generics.ListCreateAPIView, generics.DestroyAPIView):
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        authenticated request user is set as user id
        """
        serializer.save(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        """
        Deletes all menu items created by the current request user
        """
        instance = Cart.objects.filter(user=self.request.user)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrdersView(generics.ListCreateAPIView):
    """
    Returns all orders with order items created by authenticated request user
    """

    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.groups.filter(name="Delivery Crew"):
            return Order.objects.filter(delivery_crew=self.request.user)
        elif (
            self.request.user.groups.filter(name="Manager")
            or self.request.user.is_superuser
        ):
            return Order.objects.all()
        else:  # customer
            return Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        menuitem_count = Cart.objects.all().filter(user=self.request.user).count()
        if menuitem_count == 0:
            return Response({"message:": "no item in cart"})

        data = request.data.copy()
        total = self.get_total_price(self.request.user)
        data["total"] = total
        data["user"] = self.request.user.id
        order_serializer = OrderSerializer(data=data)
        if order_serializer.is_valid():
            order = order_serializer.save()

            items = Cart.objects.all().filter(user=self.request.user).all()

            for item in items.values():
                orderitem = OrderItem(
                    order=order,
                    menuitem_id=item["menuitem_id"],
                    price=item["price"],
                    quantity=item["quantity"],
                )
                orderitem.save()

            Cart.objects.all().filter(user=self.request.user).delete()

            result = order_serializer.data.copy()
            result["total"] = total
            return Response(order_serializer.data)

    def get_total_price(self, user):
        total = 0
        items = Cart.objects.all().filter(user=user).all()
        for item in items.values():
            total += item["price"]
        return total


class OrdersDetailView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def update(self, request, *args, **kwargs):
        if (
            self.request.user.groups.count() == 0
        ):  # Normal user, not belonging to any group = Customer
            return Response("Not Allowed")
        else:  # everyone else - Super Admin, Manager and Delivery Crew
            return super().update(request, *args, **kwargs)

    def get_permissions(self):
        """
        Only user from 'Manager' group can delete order
        """
        if self.request.method == "DELETE":
            self.permission_classes = [IsManager]
        return super().get_permissions()
