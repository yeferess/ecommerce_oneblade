from django.shortcuts import render, get_object_or_404
from .models import Product, Category

from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse


# def product_list(request):
#     # gt =Greater Than
#     # prefetch_related('images') es importante porque evita que Django haga una consulta a la base de datos por cada producto, sino todos en una sola consulta
#     products = Product.objects.filter(stock__gt=0).prefetch_related("images")
#     categories = Category.objects.all()
#     return render(
#         request,
#         "products/product_list.html",
#         {
#             "products": products,
#             "categories": categories,
#         },
#     )


def product_list(request):
    query = request.GET.get("q", "").strip()

    products = Product.objects.filter(stock__gt=0).prefetch_related("images")

    if query:
        products = products.filter(name__icontains=query)

    categories = Category.objects.all()
    return render(
        request,
        "products/product_list.html",
        {
            "products": products,
            "categories": categories,
            "query": query,
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


def product_search_ajax(request):
    query = request.GET.get("q", "").strip()

    if len(query) < 2:
        return JsonResponse({"results": []})

    products = Product.objects.filter(
        name__icontains=query,
        stock__gt=0,
    ).select_related("category")[:8]

    results = []
    for product in products:
        main_image = (
            product.images.filter(is_main=True).first() or product.images.first()
        )

        results.append(
            {
                "id": product.id,
                "name": product.name,
                "price": f"${product.price:,.0f}",
                "image_url": main_image.image.url if main_image else "",
                "description": product.description or "",
                "url": reverse("products:detail", args=[product.pk]),
            }
        )

    return JsonResponse({"results": results})
