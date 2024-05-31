# Installation

```shell
$ pip install django-viewcomponent
```

Then add the app into `INSTALLED_APPS` in settings.py

```python
INSTALLED_APPS = [
    ...,
    'django_viewcomponent',
]
```

Modify `TEMPLATES` section of settings.py as follows:

1. Remove `'APP_DIRS': True,`
2. add `loaders` to `OPTIONS` list and set it to following value:

```python
TEMPLATES = [
    {
        ...,
        'OPTIONS': {
            'context_processors': [
                ...
            ],
            'loaders':[(
                'django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                    'django_viewcomponent.loaders.ComponentLoader',
                ]
            )],
        },
    },
]
```

(**Optional**) To avoid loading the app in each template using ``` {% load viewcomponent_tags %} ```, you can add the tag as a `builtin` in settings.py

```python
TEMPLATES = [
    {
        ...,
        'OPTIONS': {
            'context_processors': [
                ...
            ],
            'builtins': [
                'django_viewcomponent.templatetags.viewcomponent_tags',       # new
            ]
        },
    },
]
```
