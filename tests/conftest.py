import pathlib

import pytest

from django_viewcomponent import component


def pytest_configure():
    from django.conf import settings

    settings.configure(
        SECRET_KEY="seekret",
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "mem_db"},
        },
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [pathlib.Path(__file__).parent.absolute() / "templates"],
                "APP_DIRS": False,
                "OPTIONS": {
                    "loaders": [
                        (
                            "django.template.loaders.cached.Loader",
                            [
                                "django.template.loaders.filesystem.Loader",
                                "django.template.loaders.app_directories.Loader",
                                "django_viewcomponent.loaders.ComponentLoader",
                            ],
                        )
                    ],
                    "builtins": [
                        "django_viewcomponent.templatetags.viewcomponent_tags",
                    ],
                },
            }
        ],
        INSTALLED_APPS=[
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.sites",
            "django_viewcomponent",
            "tests.testapp",
        ],
        ROOT_URLCONF="tests.testapp.urls",
        VIEW_COMPONENTS={
            "preview_base": ["previews"],
        },
    )


@pytest.fixture(autouse=True)
def cleanup_after_each_test():
    yield

    # NOTE: component.registry is global, so need to clear after each test
    component.registry.clear()


@pytest.fixture
def post():
    from tests.testapp.models import Post

    return Post.objects.create(title="test", description="test")
