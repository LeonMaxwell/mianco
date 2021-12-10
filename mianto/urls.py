from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .yasg import urlpatterns as docs_urls

urlpatterns = [
    path('', include('feed.urls')),
    path('areas/', include('area.urls')),
    path('profile/', include('profilemianto.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += docs_urls
