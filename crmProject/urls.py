from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('emergio_admin/', admin.site.urls),
    path('',include('user.urls')),
    path('',include('crmAdmin.urls')),
    path('employee/',include('crmuser.urls')),
    path('superuser/',include('superuser.urls')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
