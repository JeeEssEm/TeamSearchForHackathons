from django.apps import AppConfig

from teamsearchadmin import container


class HackathonsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hackathons"

    def ready(self):
        container.wire(modules=[".views"])

