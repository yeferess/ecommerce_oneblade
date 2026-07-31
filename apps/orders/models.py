from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F
from django.core.validators import MinValueValidator
from django.utils import timezone
from apps.products.models import Product
from django.db.models import Q


class Promotion(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", "Porcentaje"
        FIXED = "fixed", "Valor fijo"

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DiscountType.choices,
        default=DiscountType.PERCENTAGE,
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    minimum_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    is_active = models.BooleanField(
        default=True,
    )

    start_date = models.DateTimeField()

    end_date = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-minimum_purchase"]

    def __str__(self):
        return self.name

    def is_valid(self):
        """
        Verifica si la promoción puede utilizarse.
        """

        now = timezone.now()

        return self.is_active and self.start_date <= now and self.end_date >= now

    def applies_to(self, subtotal):
        """
        Determina si la promoción aplica para el subtotal recibido.
        """

        if not self.is_valid():
            return False

        return subtotal >= self.minimum_purchase

    def calculate_discount(self, subtotal):
        """
        Calcula el descuento que ofrece esta promoción.
        """

        if self.discount_value <= Decimal("0.00"):
            return Decimal("0.00")

        if self.discount_type == self.DiscountType.PERCENTAGE:
            percentage = min(
                self.discount_value,
                Decimal("100.00"),
            )
            return (subtotal * percentage) / Decimal("100.00")

        if self.discount_type == self.DiscountType.FIXED:
            return min(
                self.discount_value,
                subtotal,
            )

        return Decimal("0.00")


class Order(models.Model):
    class Status(models.TextChoices):
        CART = "cart", "Carrito"
        PENDING_PAYMENT = "pending_payment", "Pendiente de pago"
        PAID = "paid", "Pagada"
        PROCESSING = "processing", "En preparación"
        SHIPPED = "shipped", "Enviada"
        DELIVERED = "delivered", "Entregada"
        CANCELLED = "cancelled", "Cancelada"

    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", "Porcentaje"
        FIXED = "fixed", "Valor fijo"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    order_number = models.CharField(
        max_length=25,
        unique=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CART,
    )

    shipping_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    final_subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    final_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    promotion = models.ForeignKey(
        "Promotion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    # para hacer las transiciones de estado permitidas
    ALLOWED_STATUS_TRANSITIONS = {
        Status.CART: [
            Status.PENDING_PAYMENT,
        ],
        Status.PENDING_PAYMENT: [
            Status.PAID,
            Status.CANCELLED,
        ],
        Status.PAID: [
            Status.PROCESSING,
            Status.CANCELLED,
        ],
        Status.PROCESSING: [
            Status.SHIPPED,
        ],
        Status.SHIPPED: [
            Status.DELIVERED,
        ],
        Status.DELIVERED: [],
        Status.CANCELLED: [],
    }

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(status="cart"),
                name="unique_cart_per_user",
            ),
        ]

    def __str__(self):
        return self.order_number or f"Order #{self.pk}"

    # Metodos publicos

    def confirm(self):
        """
        Confirma la orden y la deja lista para el proceso de pago.
        """
        with transaction.atomic():
            self._validate_confirmation()
            self._calculate_totals()
            self._generate_order_number()
            self._deduct_stock()
            self._mark_as_pending_payment()
            self.full_clean()
            self.save()

    def add_product(self, product, quantity):
        """
        Agrega un producto a la orden.
        Si el producto ya existe, aumenta la cantidad.
        """

        if not self._can_be_modified():
            raise ValidationError("La orden no puede modificarse.")

        if quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")

        order_product = self.items.filter(product=product).first()

        current_quantity = order_product.quantity if order_product else 0
        requested_quantity = current_quantity + quantity

        if not product.is_available(requested_quantity):
            raise ValidationError(
                f"Solo hay {product.stock} unidades disponibles de '{product.name}'."
            )

        with transaction.atomic():
            if order_product:
                order_product.quantity = F("quantity") + quantity
                order_product.save(update_fields=["quantity"])
                order_product.refresh_from_db()

                return order_product

            return self.items.create(
                product=product,
                quantity=quantity,
                price=product.price,
            )

    # Calculos
    def calculate_subtotal(self):
        subtotal = Decimal("0.00")

        for item in self.items.all():
            subtotal += item.calculate_subtotal()

        return subtotal

    def calculate_total(self, subtotal, discount):
        total = subtotal - discount + self.shipping_amount
        return max(total, Decimal("0.00"))

    def can_be_modified(self):
        return self.status == self.Status.CART

    def can_change_to(self, new_status):
        """
        Determina si la orden puede cambiar al estado indicado.
        """
        return new_status in self.ALLOWED_STATUS_TRANSITIONS[self.status]

    def update_product(self, product, quantity):
        """
        Actualiza la cantidad de un producto del carrito.
        """

        if not self._can_be_modified():
            raise ValidationError("La orden no puede modificarse.")

        order_product = self.items.filter(
            product=product,
        ).first()

        if not order_product:
            raise ValidationError("El producto no existe en la orden.")

        if quantity <= 0:
            self.remove_product(product)
            return

        if not product.is_available(quantity):
            raise ValidationError(
                f"Solo hay {product.stock} unidades disponibles de '{product.name}'."
            )

        order_product.quantity = quantity
        order_product.save(
            update_fields=[
                "quantity",
            ]
        )

    def remove_product(self, product):
        """
        Elimina un producto de la orden.
        """

        if not self._can_be_modified():
            raise ValidationError("La orden no puede modificarse.")

        order_product = self.items.filter(
            product=product,
        ).first()

        if not order_product:
            raise ValidationError("El producto no existe en la orden.")

        order_product.delete()

    def _validate_confirmation(self):

        if not self._can_be_confirmed():
            raise ValidationError("Solo las órdenes en estado CART pueden confirmarse.")

        if not self.user:
            raise ValidationError("La orden debe estar asociada a un usuario.")

        if not self.items.exists():
            raise ValidationError("La orden no contiene productos.")

        for item in self.items.all():
            if item.quantity <= 0:
                raise ValidationError(
                    f"La cantidad del producto '{item.product.name}' debe ser mayor que cero."
                )

    def _can_be_confirmed(self):
        return self.status == self.Status.CART

    def _can_be_modified(self):
        """
        Solo las órdenes en estado CART pueden modificarse.
        """
        return self.status == self.Status.CART

    def _calculate_totals(self):
        """
        Calcula y almacena los totales finales de la orden.
        """

        subtotal = self.calculate_subtotal()

        promotion = self.find_best_promotion(subtotal)

        if promotion:
            discount = promotion.calculate_discount(subtotal)
        else:
            discount = Decimal("0.00")

        total = self.calculate_total(
            subtotal,
            discount,
        )

        self.promotion = promotion
        self.final_subtotal = subtotal
        self.discount_amount = discount
        self.final_total = total

    def _deduct_stock(self):
        """
        Descuenta del inventario las cantidades de los productos de la orden.
        """

        for item in self.items.select_related("product"):
            product = item.product

            if not product.is_available(item.quantity):
                raise ValidationError(
                    f"Solo hay {product.stock} unidades disponibles de '{product.name}'."
                )

            product.stock -= item.quantity
            product.save(update_fields=["stock"])

    def _generate_order_number(self):
        """
        Genera un número único para la orden.
        Formato:
        ORD-AAAAMMDD-000001
        """

        if self.order_number:
            return

        today = timezone.localdate()

        last_order = (
            Order.objects.filter(
                created_at__date=today,
                order_number__isnull=False,
            )
            .exclude(order_number="")
            .order_by("-created_at")
            .first()
        )
        sequence = 1

        if last_order:
            last_sequence = int(last_order.order_number.split("-")[-1])
            sequence = last_sequence + 1

        self.order_number = f"ORD-{today.strftime('%Y%m%d')}-{sequence:06d}"

    def _mark_as_pending_payment(self):
        self.status = self.Status.PENDING_PAYMENT

    def find_best_promotion(self, subtotal):
        """
        Busca la mejor promoción aplicable para la orden.
        """

        best_promotion = None
        best_discount = Decimal("0.00")

        promotions = Promotion.objects.filter(
            is_active=True,
        )

        for promotion in promotions:
            if not promotion.applies_to(subtotal):
                continue

            discount = promotion.calculate_discount(subtotal)

            if discount > best_discount:
                best_discount = discount
                best_promotion = promotion

        return best_promotion


class OrderProduct(models.Model):
    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_products",
    )

    quantity = models.PositiveIntegerField(
        default=1,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["id"]

        constraints = [
            models.UniqueConstraint(
                fields=["order", "product"],
                name="unique_product_per_order",
            )
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def calculate_subtotal(self):
        return self.price * self.quantity

    def _can_be_modified(self):
        """
        Determina si este producto de la orden puede modificarse.
        """
        return self.order.can_be_modified()

    def save(self, *args, **kwargs):
        """
        Evita modificar productos de una orden confirmada.
        """
        if self.pk and not self._can_be_modified():
            raise ValidationError("No es posible modificar una orden confirmada.")

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Evita eliminar productos de una orden confirmada.
        """
        if not self._can_be_modified():
            raise ValidationError(
                "No es posible eliminar productos de una orden confirmada."
            )

        super().delete(*args, **kwargs)
