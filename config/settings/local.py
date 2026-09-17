from .base import *  # noqa: F401,F403

DEBUG = True

if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
