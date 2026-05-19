import os
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings

def welcome_view(request):
    template_path = os.path.join(settings.BASE_DIR, 'healthcare_backend', 'templates', 'index.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    return HttpResponse(html_content, content_type='text/html')

def frontend_view(request):
    template_path = os.path.join(settings.BASE_DIR, 'healthcare_backend', 'templates', 'docbridge_frontend (1).html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    return HttpResponse(html_content, content_type='text/html')

urlpatterns = [
    path('', welcome_view, name='root-welcome'),
    path('frontend/', frontend_view, name='docbridge-frontend'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
