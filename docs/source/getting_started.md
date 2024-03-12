# Getting Started

Create *components/example/example.py*

```python
from django_viewcomponent import component


@component.register("example")
class ExampleComponent(component.Component):
    template_name = "example/example.html"

    def __init__(self, **kwargs):
        self.title = kwargs['title']
```

1. `template_name` is a string that contains the path to the HTML template for the component.

Create *components/example/example.html*

```django
<span title="{{ self.title }}">
  {{ self.content }}
</span>
```

Notes:

1. This is the template file for the component.
2. `self` points to the component instance itself, we can use it to access component variable and property.

Then the file structure would look like this:

```bash
components
├── example
│   ├── example.html
│   └── example.py
└── hello
    └── hello.py
```

To use the component in Django templates:

```django
{% component "example" title='my title' %}
  Hello World
{% endcomponent %}
```

Notes:

1. The **children node list** within the `component` tag will be evaluated first, passed to the component, and it can be accessed via `{{ self.content }}` in the component template.

So the final HTML would be:

```html
<span title="my title">
    Hello World
</span>
```
