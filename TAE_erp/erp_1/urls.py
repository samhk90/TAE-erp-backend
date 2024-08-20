from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [

    path('', views.index, name='index'),
    path('login/', views.login, name='login'),    
    path('attendance_form/', views.attendance_form, name='attendance_form'),
    # path('attendance_form/<int:sub>/<int:id>/<str:class_name>/', views.attendance_form, name='attendance_form'),
    path('attendance_form/<int:sub>/<int:id>/<str:class_name>/<str:batch>', views.attendance_form, name='attendance_form'),
    path('students',views.students,name='students'),
    path('notices',views.notices,name='notices'),
    path('noticeform',views.noticeform,name='noticefrom'),
    path('delete_notice',views.delete_notice,name='delete_notice'),
    path('edit_notice', views.edit_notice, name='edit_notice'),
    path('academics',views.academics,name='academics'),
    path('logout',views.logout,name='logout'),
    path('student',views.student,name='student'),
    path('greenbook',views.greenbook,name='greenbook'),
    path('logs',views.logs,name='logs')

] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)