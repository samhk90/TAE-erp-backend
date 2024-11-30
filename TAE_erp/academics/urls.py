from django.urls import path
from academics import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # Remove duplicate preacademic URL and keep only one
    path('', views.preacademic, name='preacademic_home'),
    path('attendance_form', views.attendance_form, name='attendance_form'),
    path('preacademic', views.preacademic, name='preacademic'),
    path('pre_attendance', views.pre_attendance, name='pre_attendance'),
    path('greenbook', views.greenbook, name='greenbook'),
    path('timetable', views.timetable, name='timetable'),
    path('pretest', views.pretest, name='pretest'),
    path('report', views.report, name='report'),
    path('download-csv-template/', views.download_csv_template, name='download_csv_template'),
] 

# Add static URL patterns
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)