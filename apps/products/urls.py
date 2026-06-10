from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("<int:product_id>/", views.product_detail, name="product_detail"),
    path(
        "category/<slug:category_slug>/",
        views.product_by_category,
        name="product_by_category",
    ),
]
