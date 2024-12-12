from django.apps import AppConfig

from teamsearchadmin import container


class WishesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "wishes"

    def ready(self):
        container.wire(modules=['.views'])
