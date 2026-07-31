from django.urls import path

from .views import (
    AddProductView,
    CartDetailView,
    ConfirmOrderView,
    RemoveItemView,
    UpdateItemView,
)

app_name = "orders"

urlpatterns = [
    path(
        "cart/",
        CartDetailView.as_view(),
        name="cart_detail",
    ),
    path(
        "add/<int:pk>/",
        AddProductView.as_view(),
        name="add_product",
    ),
    path(
        "update/<int:pk>/",
        UpdateItemView.as_view(),
        name="update_item",
    ),
    path(
        "remove/<int:pk>/",
        RemoveItemView.as_view(),
        name="remove_item",
    ),
    path(
        "confirm/",
        ConfirmOrderView.as_view(),
        name="confirm",
    ),
]
