# Testing

```python
template = Template(
    """
    {% load viewcomponent_tags %}
    {% component 'blog' as component %}
        {% call component.header classes='text-lg' %}
            <a href="/">My Site</a>
        {% endcall %}
        {% for post in qs %}
            {% call component.posts post=post %}{% endcall %}
        {% endfor %}
    {% endcomponent %}
    """
)
html = template.render(Context({"qs": qs}))

# check the HTML
```

You can also check the `tests` directory of this project to know more.
