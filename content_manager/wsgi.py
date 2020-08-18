"""
WSGI config for content_manager project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
from dotenv import load_dotenv
from django.core.wsgi import get_wsgi_application
from content_manager.settings import BASE_DIR

env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=env_path)
print(env_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'content_manager.production')

application = get_wsgi_application()
