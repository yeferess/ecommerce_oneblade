# Ecommerce OneBlade

## Descripción

Ecommerce OneBlade es una aplicación web desarrollada para la venta de máquinas de barbería, repuestos y accesorios. El proyecto busca ofrecer una experiencia moderna, rápida y organizada para los usuarios interesados en productos profesionales para barbería.

El sistema fue desarrollado utilizando Django debido a su rapidez para construir prototipos, su arquitectura escalable y las herramientas integradas que facilitan el desarrollo backend.

---

## Tecnologías Utilizadas

- Python 3.12
- Django 6.0.5
- SQLite
- HTML5
- Tailwind CSS
- UV
- Git / GitHub

---
Estructura del proyecto


│ecommerce_oneblade/
│
├── manage.py
├── pyproject.toml
├── uv.lock
├── .env
├── .gitignore
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── ...
│   │
│   ├── users/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── form.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── ...
│   │
│   ├── products/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── ...
│   │
│   └── orders/
│       ├── admin.py
│       ├── apps.py
│       ├── mixins.py
│       ├── models.py
│       ├── tests.py
│       ├── urls.py
│       ├── views.py
│       └── ...
│
├── static/
├── media/
└── templates/