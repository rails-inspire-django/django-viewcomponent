import pytest
from django.template import Context, Template
from django.utils.safestring import mark_safe

from django_viewcomponent import component
from django_viewcomponent.fields import RendersManyField, RendersOneField
from tests.testapp.models import Post
from tests.utils import assert_dom_equal


@pytest.mark.django_db
class TestRenderFieldComponentContextLogic:
    class HeaderComponent(component.Component):
        def __init__(self, classes, **kwargs):
            self.classes = classes

        def get_context_data(self):
            context = super().get_context_data()
            context["site_name"] = "My Site"
            return context

        template = """
            <h1 class="{{ self.classes }}">
                <a href="/"> {{ site_name }} </a>
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
        header = RendersOneField(component="header")
        posts = RendersManyField(component="post")
        wrappers = RendersManyField()

        template = """
        {% load viewcomponent_tags %}
        {{ self.header.value }}
        {% for post in self.posts.value %}
          {{ post }}
        {% endfor %}
        {% for wrapper in self.wrappers.value %}
          {{ wrapper }}
        {% endfor %}
        """

    @pytest.fixture(autouse=True)
    def register_component(self):
        component.registry.register("blog", self.BlogComponent)
        component.registry.register("header", self.HeaderComponent)
        component.registry.register("post", self.PostComponent)

    def test_field_context_logic(self):
        """
        HeaderComponent.get_context_data add extra context data

        We can still access the value via {{ site_name }}
        """

        for i in range(5):
            title = f"test {i}"
            description = f"test {i}"
            Post.objects.create(title=title, description=description)

        qs = Post.objects.all()

        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component 'blog' as component %}
                {% call component.header classes='text-lg' %}{% endcall %}
                {% for post in qs %}
                    {% call component.posts post=post %}{% endcall %}
                {% endfor %}
            {% endcomponent %}
            """,
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

    def test_field_context_logic_2(self):
        """
        can still concatenate the HTML manually and pass to slot field
        """
        for i in range(5):
            title = f"test {i}"
            description = f"test {i}"
            Post.objects.create(title=title, description=description)

        qs = Post.objects.all()

        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component 'blog' as component %}
                {% call component.header classes='text-lg' %}{% endcall %}
                {% for post in qs %}
                    {% call component.wrappers %}
                        <h1>{{ post.title }}</h1>
                        <div>{{ post.description }}</div>
                    {% endcall %}
                {% endfor %}
            {% endcomponent %}
            """,
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
class TestRenderFieldComponentParameterString:
    """
    component parameter is a component name string
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
            """,
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


class BlogComponent1(component.Component):
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
    component parameter is a Component class
    """

    @pytest.fixture(autouse=True)
    def register_component(self):
        component.registry.register("blog", BlogComponent1)

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
            """,
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
class TestRenderFieldComponentParameterLambdaReturnString:
    """
    component parameter is a lambda that returns a string
    """

    class HeaderComponent(component.Component):
        def __init__(self, classes, **kwargs):
            self.classes = classes

        template = """
            <h1 class="{{ self.classes }}">
              {{ self.content }}
            </h1>
        """

    class BlogComponent(component.Component):
        def __init__(self, **kwargs):
            self.foo = "Hello"

        header = RendersOneField(required=True, component="header")
        posts = RendersManyField(
            required=True,
            component=lambda self, post, **kwargs: mark_safe(
                f"""
                <h1>{self.foo} {post.title}</h1>
                <div>{post.description}</div>
            """,
            ),
        )

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
            """,
        )
        rendered = template.render(Context({"qs": qs}))
        expected = """
        <h1 class="text-lg">
            <a href="/">My Site</a>
        </h1>

        <h1>Hello test 0</h1>
        <div>test 0</div>

        <h1>Hello test 1</h1>
        <div>test 1</div>

        <h1>Hello test 2</h1>
        <div>test 2</div>

        <h1>Hello test 3</h1>
        <div>test 3</div>

        <h1>Hello test 4</h1>
        <div>test 4</div>
        """
        assert_dom_equal(expected, rendered)


class PostComponent2(component.Component):
    def __init__(self, post, **kwargs):
        self.post = post

    template = """
    {% load viewcomponent_tags %}

    <h1>{{ self.post.title }}</h1>
    <div>{{ self.post.description }}</div>
    """


@pytest.mark.django_db
class TestRenderFieldComponentParameterLambdaReturnInstance:
    """
    component parameter is a lambda that returns a component instance
    """

    class HeaderComponent(component.Component):
        def __init__(self, classes, **kwargs):
            self.classes = classes

        template = """
            <h1 class="{{ self.classes }}">
              {{ self.content }}
            </h1>
        """

    class BlogComponent(component.Component):
        header = RendersOneField(required=True, component="header")
        posts = RendersManyField(
            required=True,
            component=lambda post, **kwargs: PostComponent2(post=post),
        )

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
            """,
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
class TestRenderFieldTypes:
    """
    Polymorphic slots
    """

    class AvatarComponent(component.Component):
        def __init__(self, src, alt, **kwargs):
            self.src = src
            self.alt = alt

        template = """
            <img src="{{ self.src }}" alt="{{ self.alt }}">
        """

    class ListItemComponent(component.Component):
        item = RendersOneField(
            required=True,
            types={
                "avatar": "avatar",
                "span": lambda content, **kwargs: mark_safe(f"<span>{content}</span>"),
            },
        )

        template = """
            <li>{{ self.item.value }}</li>
        """

    @pytest.fixture(autouse=True)
    def register_component(self):
        component.registry.register("list_item", self.ListItemComponent)
        component.registry.register("avatar", self.AvatarComponent)

    def test_field_component_parameter(self):
        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component 'list_item' as component %}
                {% call component.item_avatar alt='username' src='http://some-site.com/my_avatar.jpg' %}{% endcall %}
            {% endcomponent %}
            {% component 'list_item' as component %}
                {% call component.item_span %}username{% endcall %}
            {% endcomponent %}
            """,
        )
        rendered = template.render(Context({}))
        expected = """
        <li>
            <img src="http://some-site.com/my_avatar.jpg" alt="username">
        </li>
        <li>
            <span>username</span>
        </li>
        """
        assert_dom_equal(expected, rendered)
