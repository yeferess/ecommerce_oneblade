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