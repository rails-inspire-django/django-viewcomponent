import pytest
from django.template import Context, Template

from django_viewcomponent import component
from django_viewcomponent.fields import RendersManyField, RendersOneField
from tests.testapp.models import Post
from tests.utils import assert_dom_equal


@pytest.mark.django_db
class TestRenderFieldComponentParameterString:
    """
    test setting component using component string

    RendersOneField(required=True, component="header")
    """

    class HeaderComponent(component.Component):
        def __init__(self, classes, **kwargs):
            self.classes = classes

        template = """
            <h1 class="{{ self.classes }}">
              {{ self.content }}
            </h1>
        """

    class PostComponent(component.Component):
        def __init__(self, post, **kwargs):
            self.post = post

        template = """
        {% load viewcomponent_tags %}

        <h1>{{ self.post.title }}</h1>
        <div>{{ self.post.description }}</div>
        """

    class BlogComponent(component.Component):
        header = RendersOneField(required=True, component="header")
        posts = RendersManyField(required=True, component="post")

        template = """
        {% load viewcomponent_tags %}
        {{ self.header.value }}
        {% for post in self.posts.value %}
          {{ post }}
        {% endfor %}
        """

    @pytest.fixture(autouse=True)
    def register_component(self):
        component.registry.register("blog", self.BlogComponent)
        component.registry.register("header", self.HeaderComponent)
        component.registry.register("post", self.PostComponent)

    def test_field_component_parameter(self):
        for i in range(5):
            title = f"test {i}"
            description = f"test {i}"
            Post.objects.create(title=title, description=description)

        qs = Post.objects.all()

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
        rendered = template.render(Context({"qs": qs}))
        expected = """
        <h1 class="text-lg">
            <a href="/">My Site</a>
        </h1>

        <h1>test 0</h1>
        <div>test 0</div>

        <h1>test 1</h1>
        <div>test 1</div>

        <h1>test 2</h1>
        <div>test 2</div>

        <h1>test 3</h1>
        <div>test 3</div>

        <h1>test 4</h1>
        <div>test 4</div>
        """
        assert_dom_equal(expected, rendered)


class BlogComponent(component.Component):
    class HeaderComponent(component.Component):
        def __init__(self, classes, **kwargs):
            self.classes = classes

        template = """
            <h1 class="{{ self.classes }}">
              {{ self.content }}
            </h1>
        """

    class PostComponent(component.Component):
        def __init__(self, post, **kwargs):
            self.post = post

        template = """
        {% load viewcomponent_tags %}

        <h1>{{ self.post.title }}</h1>
        <div>{{ self.post.description }}</div>
        """

    header = RendersOneField(required=True, component=HeaderComponent)
    posts = RendersManyField(required=True, component=PostComponent)

    template = """
    {% load viewcomponent_tags %}
    {{ self.header.value }}
    {% for post in self.posts.value %}
      {{ post }}
    {% endfor %}
    """


@pytest.mark.django_db
class TestRenderFieldComponentParameterClass:
    """
    test setting component using component Class
    """

    @pytest.fixture(autouse=True)
    def register_component(self):
        component.registry.register("blog", BlogComponent)

    def test_field_component_parameter(self):
        for i in range(5):
            title = f"test {i}"
            description = f"test {i}"
            Post.objects.create(title=title, description=description)

        qs = Post.objects.all()

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
        rendered = template.render(Context({"qs": qs}))
        expected = """
        <h1 class="text-lg">
            <a href="/">My Site</a>
        </h1>

        <h1>test 0</h1>
        <div>test 0</div>

        <h1>test 1</h1>
        <div>test 1</div>

        <h1>test 2</h1>
        <div>test 2</div>

        <h1>test 3</h1>
        <div>test 3</div>

        <h1>test 4</h1>
        <div>test 4</div>
        """
        assert_dom_equal(expected, rendered)


@pytest.mark.django_db
class TestRenderFieldComponentParameterLambda:
    """
    test setting component using component Class
    """

    @pytest.fixture(autouse=True)
    def register_component(self):
        component.registry.register("blog", BlogComponent)

    def test_field_component_parameter(self):
        for i in range(5):
            title = f"test {i}"
            description = f"test {i}"
            Post.objects.create(title=title, description=description)

        qs = Post.objects.all()

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
        rendered = template.render(Context({"qs": qs}))
        expected = """
        <h1 class="text-lg">
            <a href="/">My Site</a>
        </h1>

        <h1>test 0</h1>
        <div>test 0</div>

        <h1>test 1</h1>
        <div>test 1</div>

        <h1>test 2</h1>
        <div>test 2</div>

        <h1>test 3</h1>
        <div>test 3</div>

        <h1>test 4</h1>
        <div>test 4</div>
        """
        assert_dom_equal(expected, rendered)