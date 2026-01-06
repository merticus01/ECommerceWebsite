from django.conf import settings


def site_settings(request):
    return {
        "GOOGLE_ANALYTICS_ID": getattr(settings, "GOOGLE_ANALYTICS_ID", ""),
        "SITE_NAME": getattr(settings, "SITE_NAME", ""),
        "SITE_URL": getattr(settings, "SITE_URL", ""),
    }
