from django.shortcuts import render, get_object_or_404
from .models import Product, Category


def product_list(request):
    # gt =Greater Than
    # prefetch_related('images') es importante porque evita que Django haga una consulta a la base de datos por cada producto, sino todos en una sola consulta
    products = Product.objects.filter(stock__gt=0).prefetch_related("images")
    categories = Category.objects.all()
    return render(
        request,
        "products/product_list.html",
        {
            "products": products,
            "categories": categories,
        },
    )


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    main_image = product.images.filter(is_main=True).first()
    return render(
        request,
        "products/product_detail.html",
        {"product": product, "main_image": main_image},
    )


def product_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    Products = Product.objects.filter(category=category)
    return render(request, "products/product_list.html", {"products": Products})
