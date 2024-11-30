# project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('academics/', include(('academics.urls', 'academics'), namespace='academics')),
    path('', include(('erp_1.urls', 'erp_1'), namespace='erp_1')),

]
