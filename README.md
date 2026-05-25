# Ecommerce OneBlade

## Descripción

Ecommerce OneBlade es una aplicación web desarrollada para la venta de máquinas de barbería, repuestos y accesorios. El proyecto busca ofrecer una experiencia moderna, rápida y organizada para los usuarios interesados en productos profesionales para barbería.

El sistema fue desarrollado utilizando Django debido a su rapidez para construir prototipos, su arquitectura escalable y las herramientas integradas que facilitan el desarrollo backend.

---

## Tecnologías Utilizadas

- Python 3
- Django
- HTML5
- TailwindCSS
- Postgresqsl
- UV (gestor moderno de entornos y dependencias)

---
Estructura del proyecto


│
├── .venv/
├── manage.py
├── pyproject.toml
├── uv.lock
├── .env
├── .gitignore
│
├── config/  # configuración global Django
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   │
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/     
│   ├── users/
│   ├── products/
│   ├── orders/
│   └── payments/
│
├── templates/
│
├── static/
│
├── media/
│
└── requirements/