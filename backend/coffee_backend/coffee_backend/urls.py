from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from coffee.views import healthcheck

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/healthcheck/', healthcheck, name='healthcheck'),
    path('api/', include('coffee.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
