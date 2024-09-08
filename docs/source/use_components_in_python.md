# Use Components in Python

With django-viewcomponent, you can also create components and use them in pure Python code.

```python
class Div(component.Component):
    template_name = "layout/div.html"
    css_class = None

    def __init__(self, *fields, dom_id=None, css_class=None):
        self.fields = list(fields)
        if self.css_class and css_class:
            self.css_class += f" {css_class}"
        elif css_class:
            self.css_class = css_class
        self.dom_id = dom_id

    def get_context_data(self):
        context = super().get_context_data()
        self.fields_html = " ".join(
            [
                child_component.render_from_parent_context(context)
                for child_component in self.fields
            ]
        )
        return context
```

This is a `Div` component, it will accept a list of child components and set them in `self.fields`

In `get_context_data`, it will pass `context` to each child component and render them to HTML using `render_from_parent_context` method.

Then in `layout/div.html`, the child components will be rendered using `{{ self.fields_html|safe }}`

You can find more examples in the `tests` folder.

With this approach, you can use components in Python code like this

```python
Layout(
    Fieldset(
        "Basic Info",
        Field("first_name"),
        Field("last_name"),
        Field("password1"),
        Field("password2"),
        css_class="fieldset",
    ),
)
```
