import inspect
import os
import re
from typing import Dict, Type
from urllib.parse import urljoin

from django.urls import reverse

from django_viewcomponent.app_settings import app_settings

pattern = re.compile(r"(?<!^)(?=[A-Z])")


def public_instance_methods(cls):
    return [
        name
        for name in cls.__dict__.keys()
        if not name.startswith("__") and callable(getattr(cls, name))
    ]


def camel_to_snake(name):
    # https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    name = pattern.sub("_", name).lower()
    return name


class ViewComponentPreview:
    previews: Dict[str, Type["ViewComponentPreview"]] = {}
    preview_name = None
    preview_view_component_path = None

    def __init__(self, *args, **kwargs):
        pass

    def __init_subclass__(cls, **kwargs):
        if app_settings.SHOW_PREVIEWS:
            name = cls.__name__
            name = name.replace("Preview", "")
            new_name = camel_to_snake(name)
            ViewComponentPreview.previews[new_name] = cls
            cls.preview_name = new_name
            cls.preview_view_component_path = os.path.abspath(inspect.getfile(cls))
            cls.url = urljoin(
                reverse("django_viewcomponent:preview-index"),
                cls.preview_name + "/",
            )

    @classmethod
    def examples(cls):
        public_methods = public_instance_methods(cls)
        return public_methods

    def preview_source(self, method_name):
        method = getattr(self, method_name)
        raw_source_code = inspect.getsource(method)

        # remove 4 spaces from the beginning of each line
        lines = raw_source_code.split("\n")
        modified_lines = [line[4:] for line in lines]
        modified_string = "\n".join(modified_lines)

        return modified_string
