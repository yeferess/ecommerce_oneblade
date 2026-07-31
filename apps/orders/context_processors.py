# cuenta el numero de items en el carrito para mostrarlo en el icono
from apps.orders.models import Order


def cart(request):
    """
    Agrega la cantidad de productos diferentes
    del carrito a todos los templates.
    """

    if not request.user.is_authenticated:
        return {
            "cart_quantity": 0,
        }

    cart = Order.objects.filter(
        user=request.user,
        status=Order.Status.CART,
    ).first()

    if not cart:
        return {
            "cart_quantity": 0,
        }

    return {
        "cart_quantity": cart.items.count(),
    }
