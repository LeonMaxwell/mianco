from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from .yasg import urlpatterns as docs_urls

urlpatterns = [
    path('', include('feed.urls')),
    path('areas/', include('area.urls')),
    path('profile/', include('profilemianto.urls')),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += docs_urls
