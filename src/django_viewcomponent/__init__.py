import glob
import importlib
import importlib.util
import sys
from pathlib import Path

from django.template.engine import Engine

from django_viewcomponent.loaders import ComponentLoader


def autodiscover_components():
    # Autodetect a <component>.py file in a components dir
    current_engine = Engine.get_default()
    loader = ComponentLoader(current_engine)
    dirs = loader.get_dirs()
    for directory in dirs:
        for path in glob.iglob(str(directory / "**/*.py"), recursive=True):
            import_component_file(path)


def autodiscover_previews():
    from django_viewcomponent.app_settings import app_settings

    if app_settings.SHOW_PREVIEWS:
        preview_base_ls = [Path(p) for p in app_settings.PREVIEW_BASE]
        for directory in preview_base_ls:
            for path in glob.iglob(str(directory / "**/*.py"), recursive=True):
                import_component_file(path)


def import_component_file(path):
    MODULE_PATH = path
    MODULE_NAME = Path(path).stem
    spec = importlib.util.spec_from_file_location(MODULE_NAME, MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
