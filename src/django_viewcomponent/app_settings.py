from django.conf import settings


class AppSettings:
    def __init__(self):
        self.settings = getattr(settings, "COMPONENTS", {})


app_settings = AppSettings()
