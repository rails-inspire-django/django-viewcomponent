# Context

In Django view, developers can add extra variable to the context via `get_context_data` method. 

In the same way, we can add extra variable to the component context via `get_context_data` method.

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["var2"] = "value2"
    return context
```

Then you can get the `var2` in the component template via `{{ var2 }}`, just like other variables.

## Self

`self` points to the component instance itself, since each component has its own context, so each time the component is rendered, `self` is overwritten, and this would not cause any conflict.
