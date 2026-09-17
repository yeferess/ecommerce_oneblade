from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.orders.context_processors import cart as cart_context_processor
from apps.orders.models import Order, Promotion
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

        self.assertEqual(self.order.items.count(), 1)

        item = self.order.items.first()

        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.price, self.product.price)


class PromotionModelTestCase(TestCase):
    def setUp(self):
        self.now = timezone.now()

    def _make_promotion(self, **kwargs):
        defaults = dict(
            name="Promo",
            discount_type=Promotion.DiscountType.PERCENTAGE,
            discount_value=Decimal("10.00"),
            minimum_purchase=Decimal("0.00"),
            is_active=True,
            start_date=self.now - timedelta(days=1),
            end_date=self.now + timedelta(days=1),
        )
        defaults.update(kwargs)
        return Promotion.objects.create(**defaults)

    def test_is_valid_when_active_and_in_range(self):
        promo = self._make_promotion()
        self.assertTrue(promo.is_valid())

    def test_is_valid_false_when_inactive(self):
        promo = self._make_promotion(is_active=False)
        self.assertFalse(promo.is_valid())

    def test_is_valid_false_before_start_date(self):
        promo = self._make_promotion(
            start_date=self.now + timedelta(days=1),
            end_date=self.now + timedelta(days=2),
        )
        self.assertFalse(promo.is_valid())

    def test_is_valid_false_after_end_date(self):
        promo = self._make_promotion(
            start_date=self.now - timedelta(days=2),
            end_date=self.now - timedelta(days=1),
        )
        self.assertFalse(promo.is_valid())

    def test_applies_to_at_exact_minimum(self):
        promo = self._make_promotion(minimum_purchase=Decimal("100.00"))
        self.assertTrue(promo.applies_to(Decimal("100.00")))

    def test_applies_to_below_minimum(self):
        promo = self._make_promotion(minimum_purchase=Decimal("100.00"))
        self.assertFalse(promo.applies_to(Decimal("99.99")))

    def test_calculate_discount_percentage(self):
        promo = self._make_promotion(
            discount_type=Promotion.DiscountType.PERCENTAGE,
            discount_value=Decimal("10.00"),
        )
        self.assertEqual(promo.calculate_discount(Decimal("200.00")), Decimal("20.00"))

    def test_calculate_discount_percentage_capped_at_100(self):
        promo = self._make_promotion(
            discount_type=Promotion.DiscountType.PERCENTAGE,
            discount_value=Decimal("150.00"),
        )
        self.assertEqual(promo.calculate_discount(Decimal("200.00")), Decimal("200.00"))

    def test_calculate_discount_fixed(self):
        promo = self._make_promotion(
            discount_type=Promotion.DiscountType.FIXED,
            discount_value=Decimal("30.00"),
        )
        self.assertEqual(promo.calculate_discount(Decimal("200.00")), Decimal("30.00"))

    def test_calculate_discount_fixed_capped_at_subtotal(self):
        promo = self._make_promotion(
            discount_type=Promotion.DiscountType.FIXED,
            discount_value=Decimal("500.00"),
        )
        self.assertEqual(promo.calculate_discount(Decimal("200.00")), Decimal("200.00"))

    def test_calculate_discount_zero_when_discount_value_not_positive(self):
        promo = self._make_promotion(discount_value=Decimal("0.00"))
        self.assertEqual(promo.calculate_discount(Decimal("200.00")), Decimal("0.00"))


class OrderCartFlowTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="yefer", password="123456")
        self.category = Category.objects.create(name="Clipper", slug="clipper")
        self.product = Product.objects.create(
            category=self.category,
            name="WMARK 133",
            price=Decimal("150000"),
            stock=10,
        )
        self.order = Order.objects.create(user=self.user, status=Order.Status.CART)

    def test_add_product_with_insufficient_stock_raises(self):
        with self.assertRaises(ValidationError):
            self.order.add_product(self.product, quantity=11)

    def test_add_product_with_zero_quantity_raises(self):
        with self.assertRaises(ValidationError):
            self.order.add_product(self.product, quantity=0)

    def test_add_product_twice_increments_single_row(self):
        self.order.add_product(self.product, quantity=2)
        self.order.add_product(self.product, quantity=3)

        self.assertEqual(self.order.items.count(), 1)
        self.assertEqual(self.order.items.first().quantity, 5)

    def test_add_product_snapshots_price(self):
        self.order.add_product(self.product, quantity=1)
        item = self.order.items.first()
        original_price = item.price

        self.product.price = Decimal("999999")
        self.product.save(update_fields=["price"])

        item.refresh_from_db()
        self.assertEqual(item.price, original_price)

    def test_update_product_happy_path(self):
        self.order.add_product(self.product, quantity=1)
        self.order.update_product(self.product, quantity=4)

        self.assertEqual(self.order.items.first().quantity, 4)

    def test_update_product_zero_quantity_removes_item(self):
        self.order.add_product(self.product, quantity=1)
        self.order.update_product(self.product, quantity=0)

        self.assertEqual(self.order.items.count(), 0)

    def test_update_product_insufficient_stock_raises(self):
        self.order.add_product(self.product, quantity=1)
        with self.assertRaises(ValidationError):
            self.order.update_product(self.product, quantity=999)

    def test_update_product_missing_item_raises(self):
        with self.assertRaises(ValidationError):
            self.order.update_product(self.product, quantity=1)

    def test_remove_product_happy_path(self):
        self.order.add_product(self.product, quantity=1)
        self.order.remove_product(self.product)

        self.assertEqual(self.order.items.count(), 0)

    def test_remove_missing_product_raises(self):
        with self.assertRaises(ValidationError):
            self.order.remove_product(self.product)


class OrderCalculationsTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="yefer", password="123456")
        self.category = Category.objects.create(name="Clipper", slug="clipper")
        self.order = Order.objects.create(user=self.user, status=Order.Status.CART)

    def test_calculate_subtotal_sums_all_items(self):
        p1 = Product.objects.create(
            category=self.category, name="P1", price=Decimal("100.00"), stock=5
        )
        p2 = Product.objects.create(
            category=self.category, name="P2", price=Decimal("50.00"), stock=5
        )
        self.order.add_product(p1, quantity=2)
        self.order.add_product(p2, quantity=1)

        self.assertEqual(self.order.calculate_subtotal(), Decimal("250.00"))

    def test_calculate_total_never_goes_below_zero(self):
        total = self.order.calculate_total(Decimal("10.00"), Decimal("999.00"))
        self.assertEqual(total, Decimal("0.00"))

    def test_find_best_promotion_picks_highest_applicable_discount(self):
        now = timezone.now()

        Promotion.objects.create(
            name="Baja",
            discount_type=Promotion.DiscountType.FIXED,
            discount_value=Decimal("5.00"),
            minimum_purchase=Decimal("0.00"),
            is_active=True,
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
        )
        best = Promotion.objects.create(
            name="Alta",
            discount_type=Promotion.DiscountType.FIXED,
            discount_value=Decimal("50.00"),
            minimum_purchase=Decimal("0.00"),
            is_active=True,
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
        )
        Promotion.objects.create(
            name="Inactiva",
            discount_type=Promotion.DiscountType.FIXED,
            discount_value=Decimal("100.00"),
            minimum_purchase=Decimal("0.00"),
            is_active=False,
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
        )
        Promotion.objects.create(
            name="MinimoAlto",
            discount_type=Promotion.DiscountType.FIXED,
            discount_value=Decimal("200.00"),
            minimum_purchase=Decimal("999999.00"),
            is_active=True,
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=1),
        )

        found = self.order.find_best_promotion(Decimal("100.00"))
        self.assertEqual(found, best)


class OrderConfirmTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="yefer", password="123456")
        self.category = Category.objects.create(name="Clipper", slug="clipper")
        self.product = Product.objects.create(
            category=self.category,
            name="WMARK 133",
            price=Decimal("100.00"),
            stock=10,
        )
        self.order = Order.objects.create(user=self.user, status=Order.Status.CART)

    def test_confirm_happy_path(self):
        self.order.add_product(self.product, quantity=3)
        self.order.confirm()

        self.product.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(self.order.status, Order.Status.PENDING_PAYMENT)
        self.assertIsNotNone(self.order.order_number)
        self.assertTrue(self.order.order_number.startswith("ORD-"))
        self.assertEqual(self.product.stock, 7)
        self.assertEqual(self.order.final_subtotal, Decimal("300.00"))
        self.assertEqual(self.order.final_total, Decimal("300.00"))

    def test_confirm_fails_when_cart_empty(self):
        with self.assertRaises(ValidationError):
            self.order.confirm()

    def test_confirm_fails_when_stock_no_longer_sufficient(self):
        self.order.add_product(self.product, quantity=5)
        # simula que el stock bajó por otra vía después de agregarlo al carrito
        self.product.stock = 1
        self.product.save(update_fields=["stock"])

        with self.assertRaises(ValidationError):
            self.order.confirm()

    def test_confirm_increments_sequence_same_day(self):
        User = get_user_model()
        other_user = User.objects.create_user(username="otro", password="123456")
        other_order = Order.objects.create(user=other_user, status=Order.Status.CART)

        self.order.add_product(self.product, quantity=1)
        self.order.confirm()

        other_order.add_product(self.product, quantity=1)
        other_order.confirm()

        first_seq = int(self.order.order_number.split("-")[-1])
        second_seq = int(other_order.order_number.split("-")[-1])
        self.assertEqual(second_seq, first_seq + 1)

    def test_unique_cart_per_user_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Order.objects.create(user=self.user, status=Order.Status.CART)


class OrderStatusTransitionTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="yefer", password="123456")
        self.order = Order.objects.create(user=self.user, status=Order.Status.CART)

    def test_allowed_and_disallowed_transitions(self):
        all_statuses = list(Order.Status)

        for current_status, allowed in Order.ALLOWED_STATUS_TRANSITIONS.items():
            self.order.status = current_status
            for candidate in all_statuses:
                with self.subTest(current=current_status, candidate=candidate):
                    expected = candidate in allowed
                    self.assertEqual(self.order.can_change_to(candidate), expected)


class OrderViewsTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="yefer", password="123456")
        self.other_user = User.objects.create_user(username="otro", password="123456")
        self.category = Category.objects.create(name="Clipper", slug="clipper")
        self.product = Product.objects.create(
            category=self.category,
            name="WMARK 133",
            price=Decimal("100.00"),
            stock=10,
        )

    def test_anonymous_user_redirected_to_login(self):
        checks = [
            ("get", reverse("orders:cart_detail")),
            ("post", reverse("orders:add_product", args=[self.product.pk])),
            ("post", reverse("orders:update_item", args=[self.product.pk])),
            ("post", reverse("orders:remove_item", args=[self.product.pk])),
            ("get", reverse("orders:checkout")),
            ("post", reverse("orders:confirm")),
        ]
        for method, url in checks:
            with self.subTest(url=url):
                response = getattr(self.client, method)(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("users:login"), response.url)

    def test_add_product_action_cart_redirects_back(self):
        self.client.login(username="yefer", password="123456")
        response = self.client.post(
            reverse("orders:add_product", args=[self.product.pk]),
            {"quantity": 1, "action": "cart"},
            HTTP_REFERER=reverse("products:product_list"),
        )
        self.assertRedirects(response, reverse("products:product_list"))

    def test_add_product_action_buy_redirects_to_cart(self):
        self.client.login(username="yefer", password="123456")
        response = self.client.post(
            reverse("orders:add_product", args=[self.product.pk]),
            {"quantity": 1, "action": "buy"},
        )
        self.assertRedirects(response, reverse("orders:cart_detail"))

    def test_add_product_insufficient_stock_does_not_add_item(self):
        self.client.login(username="yefer", password="123456")
        self.client.post(
            reverse("orders:add_product", args=[self.product.pk]),
            {"quantity": 999, "action": "cart"},
        )
        cart = Order.objects.get(user=self.user, status=Order.Status.CART)
        self.assertEqual(cart.items.count(), 0)

    def test_update_item_redirects_to_cart_detail(self):
        self.client.login(username="yefer", password="123456")
        self.client.post(
            reverse("orders:add_product", args=[self.product.pk]), {"quantity": 1}
        )
        response = self.client.post(
            reverse("orders:update_item", args=[self.product.pk]), {"quantity": 3}
        )
        self.assertRedirects(response, reverse("orders:cart_detail"))

        cart = Order.objects.get(user=self.user, status=Order.Status.CART)
        self.assertEqual(cart.items.first().quantity, 3)

    def test_remove_item_redirects_to_cart_detail(self):
        self.client.login(username="yefer", password="123456")
        self.client.post(
            reverse("orders:add_product", args=[self.product.pk]), {"quantity": 1}
        )
        response = self.client.post(
            reverse("orders:remove_item", args=[self.product.pk])
        )
        self.assertRedirects(response, reverse("orders:cart_detail"))

        cart = Order.objects.get(user=self.user, status=Order.Status.CART)
        self.assertEqual(cart.items.count(), 0)

    def test_confirm_order_happy_path_redirects_to_pagepay(self):
        self.client.login(username="yefer", password="123456")
        self.client.post(
            reverse("orders:add_product", args=[self.product.pk]), {"quantity": 1}
        )
        cart = Order.objects.get(user=self.user, status=Order.Status.CART)

        response = self.client.post(reverse("orders:confirm"))

        self.assertRedirects(response, reverse("orders:pagepay", args=[cart.pk]))

    def test_confirm_order_with_empty_cart_redirects_to_checkout(self):
        self.client.login(username="yefer", password="123456")
        response = self.client.post(reverse("orders:confirm"))
        self.assertRedirects(response, reverse("orders:checkout"))

    def test_payment_page_isolated_per_user(self):
        self.client.login(username="yefer", password="123456")
        self.client.post(
            reverse("orders:add_product", args=[self.product.pk]), {"quantity": 1}
        )
        my_cart = Order.objects.get(user=self.user, status=Order.Status.CART)
        my_cart.confirm()

        self.client.logout()
        self.client.login(username="otro", password="123456")
        response = self.client.get(reverse("orders:pagepay", args=[my_cart.pk]))
        self.assertEqual(response.status_code, 404)

    def test_list_orders_excludes_cart_status(self):
        self.client.login(username="yefer", password="123456")
        self.client.post(
            reverse("orders:add_product", args=[self.product.pk]), {"quantity": 1}
        )
        cart = Order.objects.get(user=self.user, status=Order.Status.CART)
        cart.confirm()

        response = self.client.get(reverse("orders:myorders"))
        orders_in_context = list(response.context["orders"])

        self.assertNotIn(Order.Status.CART, [o.status for o in orders_in_context])
        self.assertEqual(len(orders_in_context), 1)


class CartContextProcessorTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        User = get_user_model()
        self.user = User.objects.create_user(username="yefer", password="123456")
        self.category = Category.objects.create(name="Clipper", slug="clipper")

    def test_anonymous_user_has_zero_quantity(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()

        self.assertEqual(cart_context_processor(request)["cart_quantity"], 0)

    def test_user_without_cart_has_zero_quantity(self):
        request = self.factory.get("/")
        request.user = self.user

        self.assertEqual(cart_context_processor(request)["cart_quantity"], 0)

    def test_cart_quantity_counts_distinct_products_not_units(self):
        product = Product.objects.create(
            category=self.category, name="P1", price=Decimal("10.00"), stock=10
        )
        other_product = Product.objects.create(
            category=self.category, name="P2", price=Decimal("10.00"), stock=10
        )
        cart = Order.objects.create(user=self.user, status=Order.Status.CART)
        cart.add_product(product, quantity=5)  # misma línea, no cuenta doble
        cart.add_product(other_product, quantity=1)

        request = self.factory.get("/")
        request.user = self.user

        self.assertEqual(cart_context_processor(request)["cart_quantity"], 2)
