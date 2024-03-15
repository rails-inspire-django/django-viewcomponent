from django.apps import AppConfig


class ComponentsConfig(AppConfig):
    name = "django_viewcomponent"

    def ready(self):
        self.module.autodiscover_components()
        self.module.autodiscover_previews()
