"""
URL configuration for DrGame project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.website, name='website')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='website')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounting/', include('accounting.urls')),
    path('crm/', include('crm.urls')),
    # path('dashboard/', include('dashboard.urls')),
    # path('docs/', include('docs.urls')),
    # path('hr/', include('hr.urls')),
    path('inventory/', include('inventory.urls')),
    # path('messenger/', include('messenger.urls')),
    # path('orders/', include('orders.urls')),
    # path('platform-settings/', include('platform_settings.urls')),
    # path('psn/', include('psn.urls')),
    path('task-manager/', include('task_manager.urls')),
    path('users/', include('users.urls')),
    # path('website/', include('website.urls')),
    # path('sonyaccount/', include('utils.urls')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
