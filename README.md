# README

[![PyPI version](https://badge.fury.io/py/django-viewcomponent.svg)](https://badge.fury.io/py/django-viewcomponent)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/django-viewcomponent.svg)](https://pypi.python.org/pypi/django-viewcomponent/)

django-viewcomponent is a Django library that provides a way to create reusable components for your Django project.

It is inspired by Rails [ViewComponent](https://viewcomponent.org/).

## Why use django-viewcomponent

### Single responsibility

django-viewcomponent can help developers to build reusable components from the Django templates, and make the templates more readable and maintainable.

### Testing

django-viewcomponent components are Python objects, so they can be **easily tested** without touching Django view and Django urls.

## Documentation

[Documentation](https://django-viewcomponent.readthedocs.io/en/latest/)

## FAQ

### django-viewcomponent vs django-components

1. **django-viewcomponent** is inspired by Rails [ViewComponent](https://viewcomponent.org/), focusing solely on encapsulating Django templates without concerning itself with other elements such as frontend assets or generating Django responses.
2. The `slot` field in **django-viewcomponent** can be invoked multiple times to pass collections.
3. In **django-viewcomponent**, slot fields are declared in the Python component file rather than in the template file, making the slot field more flexible and easier to maintain.
4. **django-viewcomponent** includes a preview feature that allows developers to easily create component previews.
