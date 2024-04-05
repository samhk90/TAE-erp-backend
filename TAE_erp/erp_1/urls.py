from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [

    path('',views.index,name='index'),
    path('main',views.main,name='main'),
    path('info',views.info,name='info'),
    path('info_2',views.info_2,name='info_2'),
    path('student_info',views.student_info,name='student_info'),
    path('notices',views.notices,name='notices'),
    path('noticeform',views.noticeform,name='noticefrom'),
    path('delete_notice',views.delete_notice,name='delete_notice'),
    path('edit_notice', views.edit_notice, name='edit_notice'),
    path('attendance',views.attendance,name='attendance'),
    path('signout',views.signout,name='signout'),

] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)