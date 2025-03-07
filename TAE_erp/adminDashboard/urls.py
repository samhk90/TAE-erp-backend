from django.urls import path
from adminDashboard import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'adminDashboard'  # Add this line to define the app namespace

urlpatterns = [

    path('', views.admindashboard, name='admindashboard'),

] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)