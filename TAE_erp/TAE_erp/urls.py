# project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve  # Add this import
from erp_1.views import handler404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('academics/', include(('academics.urls', 'academics'), namespace='academics')),
    path('', include(('erp_1.urls', 'erp_1'), namespace='erp_1')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Add this for serving static files in production
if not settings.DEBUG:
    urlpatterns += [
        path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}),
    ]

handler404 = 'erp_1.views.handler404'