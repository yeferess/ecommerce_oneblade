from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from decimal import Decimal
from django.views import View
from django.views.generic import DetailView

from apps.orders.mixins import CartMixin
from apps.orders.models import Order
from apps.products.models import Product


class CartDetailView(
    LoginRequiredMixin,
    CartMixin,
    DetailView,
):
    model = Order

    template_name = "orders/cart_detail.html"

    context_object_name = "order"

    def get_object(self):
        return self.get_cart()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order = self.object

        subtotal = order.calculate_subtotal()

        promotion = order.find_best_promotion(subtotal)

        if promotion:
            discount = promotion.calculate_discount(subtotal)
        else:
            discount = Decimal("0.00")

        total = order.calculate_total(
            subtotal,
            discount,
        )

        context["subtotal"] = subtotal
        context["promotion"] = promotion
        context["discount"] = discount
        context["shipping"] = order.shipping_amount
        context["total"] = total

        return context


class AddProductView(
    LoginRequiredMixin,
    CartMixin,
    View,
):
    def post(self, request, pk):

        cart = self.get_cart()

        product = get_object_or_404(
            Product,
            pk=pk,
        )

        print(request.POST.get("quantity"))
        quantity = int(
            request.POST.get(
                "quantity",
                1,
            )
        )

        action = request.POST.get(
            "action",
            "cart",
        )

        try:
            cart.add_product(
                product,
                quantity,
            )

            messages.success(
                request,
                "Producto agregado al carrito.",
            )

        except ValidationError as e:
            messages.error(
                request,
                str(e),
            )

            return redirect(
                request.META.get(
                    "HTTP_REFERER",
                    "products:product_list",
                )
            )

        if action == "buy":
            return redirect(
                "orders:cart_detail",
            )

        return redirect(
            request.META.get(
                "HTTP_REFERER",
                "products:product_list",
            )
        )


class UpdateItemView(
    LoginRequiredMixin,
    CartMixin,
    View,
):
    def post(self, request, pk):

        cart = self.get_cart()

        product = get_object_or_404(
            Product,
            pk=pk,
        )

        quantity = int(
            request.POST.get(
                "quantity",
                1,
            )
        )

        try:
            cart.update_product(
                product,
                quantity,
            )

            messages.success(
                request,
                "Carrito actualizado.",
            )

        except ValidationError as e:
            messages.error(
                request,
                str(e),
            )

        return redirect(
            "orders:cart_detail",
        )


class RemoveItemView(
    LoginRequiredMixin,
    CartMixin,
    View,
):
    def post(self, request, pk):

        cart = self.get_cart()

        product = get_object_or_404(
            Product,
            pk=pk,
        )

        try:
            cart.remove_product(
                product,
            )

            messages.success(
                request,
                "Producto eliminado.",
            )

        except ValidationError as e:
            messages.error(
                request,
                str(e),
            )

        return redirect(
            "orders:cart_detail",
        )


class ConfirmOrderView(
    LoginRequiredMixin,
    CartMixin,
    View,
):
    def post(self, request):

        cart = self.get_cart()

        try:
            cart.confirm()

            messages.success(
                request,
                "Orden confirmada correctamente.",
            )

            return redirect(
                "orders:cart_detail",
            )

        except ValidationError as e:
            messages.error(
                request,
                str(e),
            )

            return redirect(
                "orders:cart_detail",
            )
