from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.orders.models import Order
from apps.products.models import Category, Product


class OrderTestCase(TestCase):
    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username="yefer",
            password="123456",
        )

        self.category = Category.objects.create(
            name="Clipper",
            slug="clipper",
        )

        self.product = Product.objects.create(
            category=self.category,
            name="WMARK 133",
            price=Decimal("150000"),
            stock=10,
        )

        self.order = Order.objects.create(
            user=self.user,
            status=Order.Status.CART,
        )

    def test_add_new_product_to_cart(self):
        self.order.add_product(
            self.product,
            quantity=1,
        )

        self.assertEqual(
            self.order.items.count(),
            1,
        )

        item = self.order.items.first()

        self.assertEqual(
            item.product,
            self.product,
        )

        self.assertEqual(
            item.quantity,
            1,
        )

        self.assertEqual(
            item.price,
            self.product.price,
        )
