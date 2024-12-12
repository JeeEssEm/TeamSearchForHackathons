from django.apps import AppConfig

from teamsearchadmin import container


class TechnologiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "technologies"

    def ready(self):
        container.wire(modules=[".views"])
