from django.urls import path

from .views import preview_index_view, preview_view, previews_view

app_name = "django_viewcomponent"


urlpatterns = [
    path("", preview_index_view, name="preview-index"),
    path("<preview_name>/", previews_view, name="previews"),
    path("<preview_name>/<example_name>/", preview_view, name="preview"),
]
