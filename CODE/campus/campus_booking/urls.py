from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard_app.urls', namespace='dashboard')),
    path('api/auth/', include('users.urls', namespace='users')),
    path('api/resources/', include('resources.urls', namespace='resources')),
    path('', lambda request: redirect('dashboard:choose_role'), name='root_redirect'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
