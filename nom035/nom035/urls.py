from django.contrib import admin
from django.urls import path, include
from users.views import login_view, index_view

urlpatterns = [
    path('surveys/', include('surveys.urls', namespace="survey")),
    path('user/', include('users.urls', namespace="user")),
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login_view'),
    path('', index_view, name='index_view'),
]
