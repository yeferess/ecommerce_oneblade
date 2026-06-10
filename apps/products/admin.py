from django.contrib import admin
from .models import Category, Product, ProductImage


class ProducImageInline(admin.TabularInline):
    # TabularInline, para subir varias imagenes directamente desde el formulario
    model = ProductImage
    # muestra 3 campos de imagen vacios por defecto
    extra = 3


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "stock", "created_at"]
    list_filter = ["category"]
    search_fields = ["name"]
    # imagenes dentro del mismo formulario
    inlines = [ProducImageInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
