from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class UserTestCase(TestCase):
    def test_register_user(self):
        """
        Verifica que un usuario pueda registrarse correctamente.
        """

        response = self.client.post(
            reverse("users:register"),
            {
                "username": "yefer",
                "email": "yefer@test.com",
                "password1": "UnaClaveSegura123!",
                "password2": "UnaClaveSegura123!",
            },
        )

        User = get_user_model()

        self.assertEqual(response.status_code, 302)

        self.assertTrue(User.objects.filter(username="yefer").exists())

    def test_register_invalid_form(self):
        """
        Verifica que el formulario inválido vuelva a mostrar la página de registro en lugar de devolver None.
        """

        response = self.client.post(
            reverse("users:register"),
            {
                "username": "",
                "email": "correo-invalido",
                "password1": "123",
                "password2": "456",
            },
        )

        self.assertEqual(response.status_code, 200)

    def test_user_login(self):
        """
        Verifica que un usuario existente pueda iniciar sesión.
        """

        User = get_user_model()

        User.objects.create_user(
            username="yefer",
            email="yefer@test.com",
            password="12345678",
        )

        response = self.client.post(
            reverse("users:login"),
            {
                "username": "yefer",
                "password": "12345678",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            User.objects.get(username="yefer").pk,
        )

    def test_user_login_invalid_credentials(self):
        """Verifica que un usuario no pueda iniciar sesión con una contraseña incorrecta."""

        User = get_user_model()

        User.objects.create_user(
            username="yefer",
            email="yefer@test.com",
            password="12345678",
        )

        response = self.client.post(
            reverse("users:login"),
            {
                "username": "yefer",
                "password": "contraseña_incorrecta",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )
