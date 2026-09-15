from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms

INPUT_CLASS = "w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm text-gray-700 focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-light transition-all duration-200"


class RegisterForm(UserCreationForm):
    # clase para el formulario de Registro, basado en modelo User
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        # los widgets controlan como se renderiza un campo en django
        widgets = {
            "username": forms.TextInput(
                attrs={"class": INPUT_CLASS, "placeholder": "Tu usuario"}
            ),
            "email": forms.EmailInput(
                attrs={"class": INPUT_CLASS, "placeholder": "Tu Email"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update(
            {"class": INPUT_CLASS, "placeholder": "Tu contraseña"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": INPUT_CLASS, "placeholder": "Confirmar contraseña"}
        )
