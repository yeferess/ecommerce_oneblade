import json
import shutil
import tempfile
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.products.models import Category, Product, ProductImage, search_products

# GIF de 1x1 pixel válido, para no depender de un archivo real en disco.
SMALL_GIF = (
    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04"
    b"\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44"
    b"\x01\x00\x3b"
)


class CategoryModelTestCase(TestCase):
    def test_str_returns_name(self):
        category = Category.objects.create(name="Clipper", slug="clipper")
        self.assertEqual(str(category), "Clipper")

    def test_name_must_be_unique(self):
        Category.objects.create(name="Clipper", slug="clipper")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Category.objects.create(name="Clipper", slug="clipper-2")

    def test_slug_must_be_unique(self):
        Category.objects.create(name="Clipper", slug="clipper")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Category.objects.create(name="Otra", slug="clipper")

    def test_slug_is_required_on_full_clean(self):
        """No hay auto-slugify: el slug debe suministrarse explícitamente."""
        category = Category(name="Sin slug")
        with self.assertRaises(ValidationError):
            category.full_clean()


class ProductModelTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Clipper", slug="clipper")

    def test_negative_stock_is_clamped_to_zero_on_save(self):
        product = Product(
            category=self.category,
            name="WMARK 133",
            price=Decimal("150000"),
            stock=-5,
        )
        product.save()
        self.assertEqual(product.stock, 0)

    def test_is_available_exact_stock(self):
        product = Product.objects.create(
            category=self.category, name="P1", price=Decimal("100"), stock=5
        )
        self.assertTrue(product.is_available(5))

    def test_is_available_more_than_stock(self):
        product = Product.objects.create(
            category=self.category, name="P1", price=Decimal("100"), stock=5
        )
        self.assertFalse(product.is_available(6))

    def test_is_available_zero_quantity(self):
        product = Product.objects.create(
            category=self.category, name="P1", price=Decimal("100"), stock=0
        )
        self.assertTrue(product.is_available(0))

    def test_is_available_zero_stock(self):
        product = Product.objects.create(
            category=self.category, name="P1", price=Decimal("100"), stock=0
        )
        self.assertFalse(product.is_available(1))

    def test_product_without_category_is_still_usable(self):
        product = Product.objects.create(
            category=None, name="Huerfano", price=Decimal("100"), stock=1
        )
        self.assertEqual(str(product), "Huerfano")
        self.assertIsNone(product.category)


class SearchProductsFunctionTestCase(TestCase):
    """`search_products()` no la usa ninguna vista, pero es API pública del módulo."""

    def setUp(self):
        category = Category.objects.create(name="Clipper", slug="clipper")
        self.p1 = Product.objects.create(
            category=category,
            name="WMARK 133",
            description="Repuesto original importado",
            price=Decimal("100"),
            stock=5,
        )
        self.p2 = Product.objects.create(
            category=category,
            name="Cuchilla X2",
            description="Compatible con maquinas WMARK",
            price=Decimal("50"),
            stock=5,
        )

    def test_empty_query_returns_all(self):
        self.assertEqual(search_products("").count(), 2)

    def test_matches_by_name_only(self):
        results = search_products("133")
        self.assertIn(self.p1, results)
        self.assertNotIn(self.p2, results)

    def test_matches_by_description_only(self):
        results = search_products("compatible")
        self.assertIn(self.p2, results)
        self.assertNotIn(self.p1, results)

    def test_no_match_returns_empty_queryset(self):
        self.assertEqual(search_products("no-existe").count(), 0)


class ProductListViewTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Clipper", slug="clipper")

    def test_excludes_out_of_stock_products(self):
        in_stock = Product.objects.create(
            category=self.category, name="Disponible", price=Decimal("100"), stock=5
        )
        Product.objects.create(
            category=self.category, name="Agotado", price=Decimal("100"), stock=0
        )

        response = self.client.get(reverse("products:product_list"))
        products = list(response.context["products"])

        self.assertEqual(products, [in_stock])

    def test_search_filters_by_name_only(self):
        """A diferencia de search_products(), la vista no busca en description."""
        Product.objects.create(
            category=self.category,
            name="Alpha",
            description="contiene beta",
            price=Decimal("10"),
            stock=1,
        )
        beta = Product.objects.create(
            category=self.category,
            name="Beta",
            description="sin coincidencia",
            price=Decimal("10"),
            stock=1,
        )

        response = self.client.get(reverse("products:product_list"), {"q": "beta"})

        self.assertEqual(list(response.context["products"]), [beta])

    def test_context_includes_all_categories_regardless_of_filter(self):
        Category.objects.create(name="Trimmer", slug="trimmer")
        response = self.client.get(reverse("products:product_list"))
        self.assertEqual(response.context["categories"].count(), 2)

    def test_search_with_no_matches_returns_empty_list(self):
        response = self.client.get(reverse("products:product_list"), {"q": "no-existe"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["products"]), [])


class ProductDetailViewTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Clipper", slug="clipper")

    def test_returns_404_for_missing_product(self):
        response = self.client.get(reverse("products:product_detail", args=[999999]))
        self.assertEqual(response.status_code, 404)

    def test_out_of_stock_product_is_still_visible(self):
        product = Product.objects.create(
            category=self.category, name="Agotado", price=Decimal("100"), stock=0
        )
        response = self.client.get(reverse("products:product_detail", args=[product.pk]))
        self.assertEqual(response.status_code, 200)

    def test_main_image_is_none_without_images(self):
        product = Product.objects.create(
            category=self.category, name="Sin imagen", price=Decimal("100"), stock=1
        )
        response = self.client.get(reverse("products:product_detail", args=[product.pk]))
        self.assertIsNone(response.context["main_image"])


class ProductByCategoryViewTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Clipper", slug="clipper")

    def test_returns_404_for_missing_slug(self):
        response = self.client.get(
            reverse("products:product_by_category", args=["no-existe"])
        )
        self.assertEqual(response.status_code, 404)

    def test_empty_category_returns_empty_list(self):
        response = self.client.get(
            reverse("products:product_by_category", args=[self.category.slug])
        )
        self.assertEqual(list(response.context["products"]), [])

    def test_includes_out_of_stock_products_unlike_product_list(self):
        """product_by_category no filtra por stock, a diferencia de product_list."""
        product = Product.objects.create(
            category=self.category, name="Agotado", price=Decimal("100"), stock=0
        )
        response = self.client.get(
            reverse("products:product_by_category", args=[self.category.slug])
        )
        self.assertIn(product, list(response.context["products"]))


class ProductSearchAjaxViewTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Clipper", slug="clipper")

    def test_missing_query_returns_empty_results(self):
        response = self.client.get(reverse("products:search_ajax"))
        self.assertEqual(json.loads(response.content), {"results": []})

    def test_single_character_query_returns_empty_results(self):
        response = self.client.get(reverse("products:search_ajax"), {"q": "a"})
        self.assertEqual(json.loads(response.content), {"results": []})

    def test_excludes_out_of_stock_products(self):
        Product.objects.create(
            category=self.category, name="Wmark agotado", price=Decimal("100"), stock=0
        )
        response = self.client.get(reverse("products:search_ajax"), {"q": "wmark"})
        self.assertEqual(json.loads(response.content)["results"], [])

    def test_limits_results_to_eight(self):
        for i in range(9):
            Product.objects.create(
                category=self.category, name=f"Wmark {i}", price=Decimal("100"), stock=1
            )
        response = self.client.get(reverse("products:search_ajax"), {"q": "wmark"})
        self.assertEqual(len(json.loads(response.content)["results"]), 8)

    def test_result_url_resolves_to_product_detail(self):
        product = Product.objects.create(
            category=self.category, name="Wmark 133", price=Decimal("100"), stock=1
        )
        response = self.client.get(reverse("products:search_ajax"), {"q": "wmark"})
        result = json.loads(response.content)["results"][0]
        self.assertEqual(
            result["url"], reverse("products:product_detail", args=[product.pk])
        )

    def test_image_url_defaults_to_empty_string_without_images(self):
        Product.objects.create(
            category=self.category, name="Wmark sin imagen", price=Decimal("100"), stock=1
        )
        response = self.client.get(reverse("products:search_ajax"), {"q": "wmark"})
        result = json.loads(response.content)["results"][0]
        self.assertEqual(result["image_url"], "")


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
        },
    }
)
class ProductImageModelTestCase(TestCase):
    """
    Usa FileSystemStorage + un MEDIA_ROOT temporal para no intentar subir
    archivos de verdad a Cloudinary durante los tests.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._tmp_media_root = tempfile.mkdtemp()
        cls._media_root_override = override_settings(MEDIA_ROOT=cls._tmp_media_root)
        cls._media_root_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._media_root_override.disable()
        shutil.rmtree(cls._tmp_media_root, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        category = Category.objects.create(name="Clipper", slug="clipper")
        self.product = Product.objects.create(
            category=category, name="WMARK 133", price=Decimal("100"), stock=5
        )

    def _uploaded_gif(self, name="test.gif"):
        return SimpleUploadedFile(name, SMALL_GIF, content_type="image/gif")

    def test_multiple_main_images_are_allowed(self):
        """No hay enforcement de 'solo una imagen principal por producto'."""
        ProductImage.objects.create(
            product=self.product, image=self._uploaded_gif("a.gif"), is_main=True
        )
        ProductImage.objects.create(
            product=self.product, image=self._uploaded_gif("b.gif"), is_main=True
        )
        self.assertEqual(self.product.images.filter(is_main=True).count(), 2)

    def test_first_main_image_is_none_when_none_marked(self):
        ProductImage.objects.create(
            product=self.product, image=self._uploaded_gif("a.gif"), is_main=False
        )
        self.assertIsNone(self.product.images.filter(is_main=True).first())

    def test_first_main_image_when_one_marked(self):
        img = ProductImage.objects.create(
            product=self.product, image=self._uploaded_gif("a.gif"), is_main=True
        )
        self.assertEqual(self.product.images.filter(is_main=True).first(), img)
