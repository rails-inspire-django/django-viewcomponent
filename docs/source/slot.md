# Slots

If we want to pass more than one content block to the component, `self.content` is not enough, we can use `slots` to achieve this.

Unlike other packages which declare slot via `{% slot %}`, we define the slot in the component class, just like what we defined fields in the Django model

## Basic

Create *components/blog/blog.py*

```python
from django_viewcomponent import component
from django_viewcomponent.fields import RendersOneField


@component.register("blog")
class BlogComponent(component.Component):
    header = RendersOneField(required=True)

    template = """
        {% load viewcomponent_tags %}
        
        {{ self.header.value }}
    """
```

Notes:

1. `header` is a `RendersOneField` field, it means it can only render one content block, and it is `required`.
2. `self.header.value` means render the `header` slot field, please note `value` is needed here.

To use the component in Django templates:

```django
{% component "blog" as blog_component %}
  {% call blog_component.header %}
    <a href="/">My Site</a>
  {% endcall %}
{% endcomponent %}
```

Notes:

1. `call blog_component.header` means we call the slot field `header` of the `blog_component`
2. The returning HTML would be:

```html
<a href="/">My Site</a>
```

## Check if the slot is filled

You can use `filled` attribute of the slot field to check if the slot is filled or not.

```django
{% if self.header.filled %}
    {{ self.header.value }}
{% else %}
    Default title
{% endif %}
```

## Render multiple slots

Let's update `BlogComponent`

```python
from django_viewcomponent import component
from django_viewcomponent.fields import RendersOneField, RendersManyField


@component.register("blog")
class BlogComponent(component.Component):
    header = RendersOneField(required=True)
    posts = RendersManyField(required=True)        # new

    template = """
        {% load viewcomponent_tags %}
        
        {{ self.header.value }}
        
        {% for post in self.posts.value %}
            {{ post }} 
        {% endfor %}
    """
```

Notes:

1. `posts` is a `RendersManyField` field, it means it can render multiple content blocks, and it is `required`.
2. We use `{% for post in self.posts.value %}` to iterate the `posts` slot field.

To use the component in Django templates:

```django
{% component "blog" as blog_component %}
  {% call blog_component.header %}
    <a href="/">My Site</a>
  {% endcall %}

  {% call blog_component.posts %}
    <a href="/">Post 1</a>
  {% endcall %}
  {% call blog_component.posts %}
    <a href="/">Post 2</a>
  {% endcall %}

{% endcomponent %}
```

Notes:

1. We can call `blog_component.posts` multiple times to pass the block content to the slot field `posts`.

```html
<a href="/">My Site</a>
<a href="/">Post 1</a>
<a href="/">Post 2</a>
```

## Linking slots with other component

This is a very powerful feature, please read it carefully.

Let's update the `BlogComponent` again

```python
from django_viewcomponent import component
from django_viewcomponent.fields import RendersOneField, RendersManyField


@component.register("header")
class HeaderComponent(component.Component):
    def __init__(self, classes, **kwargs):
        self.classes = classes

    template = """
        <h1 class="{{ self.classes }}">
          {{ self.content }}
        </h1>
    """


@component.register("blog")
class BlogComponent(component.Component):
    header = RendersOneField(required=True, component='header')
    posts = RendersManyField(required=True)

    template = """
        {% load viewcomponent_tags %}
        
        {{ self.header.value }}
        
        {% for post in self.posts.value %}
            {{ post }} 
        {% endfor %}
    """
```

Notes:

1. We added a `HeaderComponent`, which accept a `classes` argument
2. `header = RendersOneField(required=True, component='header')` means when `{{ self.header.value }}` is rendered, it would use the `HeaderComponent` to render the content.

```django
{% component "blog" as blog_component %}

  {% call blog_component.header classes='text-lg' %}
    <a href="/">My Site</a>
  {% endcall %}

  {% call blog_component.posts %}
    <a href="/">Post 1</a>
  {% endcall %}
  {% call blog_component.posts %}
    <a href="/">Post 2</a>
  {% endcall %}

{% endcomponent %}
```

Notes:

1. When we call `blog_component.header`, the `classes` argument is passed to the `HeaderComponent` automatically.

The final HTML would be

```html
<h1 class="text-lg">
  <a href="/">My Site</a>
</h1>
<a href="/">Post 1</a>
<a href="/">Post 2</a>
```

Notes:

1. We do not need to store the `classes` to the `BlogComponent` and then pass it to the `HeaderComponent`, just set `component='header'` in the `RendersOneField` field, the `HeaderComponent` would receive the `classes` argument automatically
2. If you check the template code in the `BlogComponent`, `{{ self.header.value }}` ia very simple to help you understand what it is.

## Component with RendersManyField

If you have

```python
posts = RendersManyField(required=True, component="post")
```

In the view template

```django
{% component 'blog' as component %}
    {% call component.header classes='text-lg' %}
        <a href="/">My Site</a>
    {% endcall %}
    {% for post in qs %}
        {% call component.posts post=post %}{% endcall %}
    {% endfor %}
{% endcomponent %}
```

Notes:

1. `qs` is a Django queryset, we iterate the queryset and fill the slot `posts` multiple times, `post` is also passed to the `PostComponent` automatically.

The `PostComponent` can be:

```python
class PostComponent(component.Component):
    def __init__(self, post, **kwargs):
        self.post = post

    template = """
    {% load viewcomponent_tags %}

    <h1>{{ self.post.title }}</h1>
    """
```
