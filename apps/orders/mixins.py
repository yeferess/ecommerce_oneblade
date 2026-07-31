from apps.orders.models import Order


class CartMixin:
    """
    Proporciona acceso al carrito activo del usuario.
    """

    def get_cart(self):
        """
        Obtiene el carrito activo del usuario autenticado.
        Si no existe, lo crea.
        """

        cart, created = Order.objects.get_or_create(
            user=self.request.user,
            status=Order.Status.CART,
        )

        return cart
