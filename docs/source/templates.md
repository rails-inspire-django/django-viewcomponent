# Templates

## Inline template

You can use `template` variable to define the template inline.

## Template file

To use an external template file, set the `template_name` variable

## Dynamic template

You can use `get_template_names` method to do dynamic template selection.

```python
class SvgComponent(component.Component):
    def __init__(self, name, **kwargs):
        self.name = name

    def get_template_name(self):
        return f"svg_{self.name}.svg"
```
