from django.apps import AppConfig
from teamsearchadmin import container


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"

    def ready(self):
        container.wire(modules=[".views"])
