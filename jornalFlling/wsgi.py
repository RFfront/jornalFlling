"""
WSGI config for jornalFlling project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jornalFlling.settings')
# import socketio
# from fillJ.views import sio
#
# django_app = get_wsgi_application()
# application = socketio.WSGIApp(sio, django_app)
application = get_wsgi_application()
