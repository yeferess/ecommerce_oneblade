from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    # slug se usa para crear urls mas legibles, ejemplo /categorias/cuidado-personal
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categorías"


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    name = models.CharField(max_length=100, verbose_name="name")
    description = models.TextField(blank=True, verbose_name="description")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="price")
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def is_available(self, quantity):
        """
        Retorna True si hay suficiente stock.
        """
        return self.stock >= quantity

    def save(self, *args, **kwargs):
        if self.stock < 0:
            # evitando valores negativos
            self.stock = 0
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/")
    # para la imagen principal
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Imagen de  {self.product.name}"
