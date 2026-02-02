from django.apps import AppConfig


class ProConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pro"

    def ready(self):
        """Load signal handlers when app is ready."""
        import apps.pro.signals  # noqa: F401
