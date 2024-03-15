from django.conf import settings


class AppSettings:
    def __init__(self):
        self.settings = getattr(settings, "VIEW_COMPONENTS", {})

    @property
    def PREVIEW_BASE(self):
        return self.settings.setdefault("preview_base", [])

    @property
    def SHOW_PREVIEWS(self):
        return self.settings.setdefault("show_previews", True)


app_settings = AppSettings()
