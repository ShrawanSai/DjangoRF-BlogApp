from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class EventsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_apps.events'
    verbose_name = _("Events")

    def ready(self):
        from core_apps.events import signals
