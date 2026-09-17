from .base import *  # noqa: F401,F403

DEBUG = False

# Railway termina el TLS en su proxy y reenvía la petición por HTTP plano
# hacia tu contenedor. Sin este header, Django no reconoce la conexión
# como segura.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7  # 1 semana para empezar
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
