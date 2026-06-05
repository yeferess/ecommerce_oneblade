from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .form import RegisterForm


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenido {user.username}!")
            return redirect("core:home")
        else:
            messages.error(request, "por favor corrija los errores")

    else:
        # redirige al formulario de registro
        form = RegisterForm()
        return render(request, "users/register.html", {"form": form})


def user_loguin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        # busca en la base de datos usando el hash
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("core:home")
        else:
            messages.error(request, "usuario o contraseña incorrectos.")
    return render(request, "users/login.html")


def user_logout(request):
    logout(request)
    return redirect("core:home")
