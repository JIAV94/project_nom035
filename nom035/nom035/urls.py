from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404, handler500
from users.views import login_view, index_view, user_logout, _404, _500

urlpatterns = [
    path('surveys/', include('surveys.urls', namespace="survey")),
    path('user/', include('users.urls', namespace="user")),
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login_view'),
    path('logout/', user_logout, name='user_logout'),
    path('', index_view, name='index_view'),
]

handler404 = _404
handler500 = _500