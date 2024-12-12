from django.apps import AppConfig

from teamsearchadmin import container


class QuestionaryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "questionary"

    def ready(self):
        container.wire(modules=['.views'])
