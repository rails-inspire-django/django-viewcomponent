# NameSpace

If your project has many components and want them to be organized in a better way, you can use the namespace feature.

```bash
├── components
│   └── testapp                    # this is the namespace
│       └── example
│           ├── example.html
│           └── example.py
```

```python
from django_viewcomponent import component


@component.register("testapp.example")
class ExampleComponent(component.Component):

    template_name = "testapp/example/example.html"

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'World')
```

You can register the component as `testapp.example`

```html
{% load viewcomponent_tags %}

{% component 'testapp.example' name="MichaelYin"%}
{% endcomponent %}
```

To use the component in Django template, you can use `component 'testapp.example'`

Notes:

1. This can help keep the components organized.
2. If you are developing 3-party Django package (`foo`), you can put all components in the `foo` namespace and use them in the package templates, this would not cause conflicts with other components in the project.
