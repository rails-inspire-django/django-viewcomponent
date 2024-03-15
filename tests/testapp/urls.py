# Django
from django.urls import path, include


urlpatterns = [
    path("previews/", include("django_viewcomponent.urls"))
]
