from django.urls import path

from . import views

urlpatterns = [
    path("menu-items/", views.MenuItemsView.as_view()),
    path("menu-items/<int:pk>/", views.SingleMenuItemView.as_view()),
    path("category/", views.CategoryView.as_view()),
    path("groups/", views.GroupView.as_view()),
    path(
        "groups/manager/users/",
        views.ManagerGroupViewSet.as_view(
            {"get": "list", "post": "create", "delete": "destroy"}
        ),
    ),
    path(
        "groups/delivery-crew/users/",
        views.DeliveryCrewGroupViewSet.as_view(
            {"get": "list", "post": "create", "delete": "destroy"}
        ),
    ),
    path("cart/menu-items/", views.CartMenuItemView.as_view()),
    path("orders/", views.OrdersView.as_view()),
    path("orders/<int:pk>/", views.OrdersDetailView.as_view()),
]
