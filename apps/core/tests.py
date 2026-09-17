from django.test import TestCase
from django.urls import resolve, reverse


class HomeViewTestCase(TestCase):
    def test_home_returns_200(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)

    def test_home_uses_expected_template(self):
        response = self.client.get(reverse("core:home"))
        self.assertTemplateUsed(response, "core/home.html")

    def test_home_renders_without_any_product_data(self):
        """
        Los enlaces a categorías del home usan slugs hardcodeados vía
        {% url %}, que solo resuelve el patrón de URL y no consulta la BD,
        así que la página debe renderizar sin necesidad de Category/Product.
        """
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)

    def test_home_is_site_root(self):
        self.assertEqual(resolve("/").view_name, "core:home")
