from django.conf import settings


def site_settings(request):
    """Expose beberapa setting situs ke semua template."""
    return {
        "GOOGLE_ANALYTICS_ID": getattr(settings, "GOOGLE_ANALYTICS_ID", ""),
    }
