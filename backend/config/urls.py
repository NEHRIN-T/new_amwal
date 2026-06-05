from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("", lambda request: redirect("admin:index")),
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/client/", include("properties.client_urls")),
    path("api/backend/", include("properties.backend_urls")),
    path("api/backend/", include("tenants.urls")),
    path("api/backend/", include("rents.urls")),
    path("api/backend/", include("occupancy.urls")),
    path("api/backend/", include("financials.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
