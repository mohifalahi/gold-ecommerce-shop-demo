from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view


def trigger_error(request):
    division_by_zero = 1 / 0

urls = [
    path('wallet/', include('base.urls.wallet')),
    path('order/', include('base.urls.order')),
    path('product/', include('base.urls.product')),
    path('transaction/', include('base.urls.transaction')),
]

urlpatterns = [
    # Route TemplateView to serve Swagger UI template.
    #   * Provide `extra_context` with view name of `SchemaView`.
    path(
        "swagger-ui/",
        TemplateView.as_view(
            template_name="swagger-ui.html",
            extra_context={"schema_url": "openapi-schema"},
        ),
        name="swagger-ui",
    ),
    # Use the `get_schema_view()` helper to add a `SchemaView` to project URLs.
    #   * `title` and `description` parameters are passed to `SchemaGenerator`.
    #   * Provide view name for use with `reverse()`.
    path('openapi', get_schema_view(
        title="Your Project",
        description="API for all things …",
        version="1.0.0"
    ), name='openapi-schema'),
    
    path('sentry-debug/', trigger_error),

    path('admin/', admin.site.urls),
    
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/', include(urls)),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
