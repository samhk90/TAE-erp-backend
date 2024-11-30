from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [

    path('', views.index, name='index'),
    path('login/', views.login, name='login'),    
    # path('attendance_form', views.attendance_form, name='attendance_form'),
    path('index',views.index,name='index'),
    path('students',views.students,name='students'),
    path('notices',views.notices,name='notices'),
    path('delete_notice/<int:id>/', views.delete_notice, name='delete_notice'),
    # path('academics',views.academics,name='academics'),
    path('logout',views.logout,name='logout'),
    path('student',views.student,name='student'),
    # path('greenbook',views.greenbook,name='greenbook'),
    path('logs',views.logs,name='logs'),
   # path('history',views.history,name='history'),
    # path('report',views.report,name='report'),
    # path('preacademic',views.preacademic,name='preacademic'),
    path('preports',views.preports,name='preports'),
    path('custom_report',views.custom_report,name='custom_report'),
    path('daily_report',views.daily_report,name='daily_report'),
    path('weekly_report',views.weekly_report,name='weekly_report'),
    path('monthly_report',views.monthly_report,name='monthly_report'),
    path('subjectwise',views.subjectwise_report,name='subjectwise'),
    path('class_report',views.class_report,name='class_report'),
    path('download-csv-template/', views.download_csv_template, name='download_csv_template'),
    

] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)