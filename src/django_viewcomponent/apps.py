from django.apps import AppConfig


class ComponentsConfig(AppConfig):
    name = "django_viewcomponent"

    def ready(self):
        # autodiscover components
        self.module.autodiscover()
