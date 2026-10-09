"""
ASGI config for smartinventory project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartinventory.settings')

application = get_asgi_application()
