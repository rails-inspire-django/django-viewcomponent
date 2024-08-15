# Overview

django-viewcomponent is a Django library that provides a way to create reusable components for your Django project. It is inspired by [ViewComponent](https://viewcomponent.org/) for Ruby on Rails.

<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; height: auto;">
        <iframe src="https://www.youtube.com/embed/QoetqsBCsbE?si=UhvtKpOLSCNcnIbW&amp;start=624" frameborder="0" allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe>
</div>

## What’s a django-viewcomponent

django-viewcomponent is an evolution of the Django partial template, a django-viewcomponent is actually a Python object.

```python
from django_viewcomponent import component

@component.register("hello")
class HelloComponent(component.Component):
    template = "<h1>Hello, {{ self.name }}!</h1>"

    def __init__(self, **kwargs):
        self.title = kwargs['title']
```

Notes:

1. Here we defined a Python class `HelloComponent` that inherits from `django_viewcomponent.component.Component`.
2. `@component.register("hello")` is a decorator that registers the component with the name `hello`.
3. The `template` attribute is a string that contains the HTML template for the component.
4. The `__init__` method is the constructor of the component, it receives the `name` parameter and stores it in the `self.name` attribute. So we can access it later in the template via `{{ self.name }}`.

To use the component in Django templates:

```django
{% load viewcomponent_tags %}

{% component "hello" name='Michael Yin' %}{% endcomponent %}
```

The `component` tag will initialize the component, and pass the `name` parameter to the `HelloComponent` constructor.

The returning HTML would be:

```html
<h1>Hello, Michael Yin!</h1>
```

## Why use django-viewcomponent

### Single responsibility

django-viewcomponent can help developers to build reusable components from the Django templates, and make the templates more readable and maintainable.

### Testing

django-viewcomponent components are Python objects, so they can be **easily tested** without touching Django view and Django urls.
