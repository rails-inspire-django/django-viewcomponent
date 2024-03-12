import pytest
from django.template import Context, Template, TemplateSyntaxError

import django_viewcomponent
import django_viewcomponent.component_registry
from django_viewcomponent import component
from django_viewcomponent.fields import RendersManyField, RendersOneField
from tests.testapp.models import Post
from tests.utils import assert_dom_equal


class SimpleComponent(component.Component):
    template_name = "simple_template.html"

    def __init__(self, **kwargs):
        self.kwargs = kwargs


class IfVariableComponent(SimpleComponent):
    template_name = "if_variable_template.html"

    def __init__(self, **kwargs):
        self.kwargs = kwargs


class SlottedComponent(component.Component):
    header = RendersOneField()
    main = RendersOneField()
    footer = RendersOneField()

    template_name = "slotted_template.html"


class BrokenComponent(component.Component):
    template_name = "template_with_illegal_slot.html"


class NonUniqueSlotsComponent(component.Component):
    template_name = "template_with_nonunique_slots.html"


class SlottedComponentWithMissingVariable(component.Component):
    header = RendersOneField()
    main = RendersOneField()
    footer = RendersOneField()

    template_name = "slotted_template_with_missing_variable.html"


class SlottedComponentNoSlots(component.Component):
    template = "<custom-template></custom-template>"


class SlottedComponentWithContext(component.Component):
    header = RendersOneField()
    main = RendersOneField()
    footer = RendersOneField()

    template_name = "slotted_template.html"

    def __init__(self, **kwargs):
        self.variable = kwargs.pop("variable")

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["variable"] = self.variable
        return context


class CalendarComponent(component.Component):
    """Nested in ComponentWithNestedComponent"""

    header = RendersOneField()
    body = RendersOneField()

    template_name = "slotted_component_nesting_template_pt1_calendar.html"


class DashboardComponent(component.Component):
    header = RendersOneField()

    template_name = "slotted_component_nesting_template_pt2_dashboard.html"


class TestComponentTemplateTag:
    def test_single_component(self):
        component.registry.register(name="test", component=SimpleComponent)

        simple_tag_template = """
            {% load viewcomponent_tags %}
            {% component "test" variable="variable" %}{% endcomponent %}
        """

        template = Template(simple_tag_template)
        assert_dom_equal(
            "Variable: <strong>variable</strong>", template.render(Context())
        )

    def test_call_with_invalid_name(self):
        """
        Calling unregistered component should raise an error
        """
        simple_tag_template = """
            {% load viewcomponent_tags %}
            {% component "test" variable="variable" %}{% endcomponent %}
        """

        template = Template(simple_tag_template)
        with pytest.raises(django_viewcomponent.component_registry.NotRegistered):
            template.render(Context({}))

    def test_component_content(self):
        """
        if pass HTML to the component without fill tags, it will be available in self.content
        """

        class Component(component.Component):
            template = "<div>{{ self.content }}</div>"

        component.registry.register("test", Component)
        simple_tag_template = """
            {% load viewcomponent_tags %}
            {% component 'test' %}
                Hello World
            {% endcomponent %}
        """
        template = Template(simple_tag_template)
        rendered = template.render(Context({}))
        assert_dom_equal(rendered, "<div>Hello World</div>")

    def test_component_called_with_positional_name(self):
        component.registry.register(name="test", component=SimpleComponent)

        simple_tag_template = """
            {% load viewcomponent_tags %}
            {% component "test" variable="variable" %}{% endcomponent %}
        """
        template = Template(simple_tag_template)
        rendered = template.render(Context({}))
        assert_dom_equal(rendered, "Variable: <strong>variable</strong>")

    def test_component_called_with_singlequoted_name(self):
        component.registry.register(name="test", component=SimpleComponent)

        simple_tag_template = """
            {% load viewcomponent_tags %}
            {% component 'test' variable="variable" %}{% endcomponent %}
        """

        template = Template(simple_tag_template)
        rendered = template.render(Context({}))
        assert_dom_equal(rendered, "Variable: <strong>variable</strong>\n")

    def test_component_called_with_variable_as_name(self):
        component.registry.register(name="test", component=SimpleComponent)

        simple_tag_template = """
            {% load viewcomponent_tags %}
            {% with component_name="test" %}
                {% component component_name variable="variable" %}{% endcomponent %}
            {% endwith %}
        """
        template = Template(simple_tag_template)
        rendered = template.render(Context({}))
        assert_dom_equal(rendered, "Variable: <strong>variable</strong>\n")

    def test_component_called_with_invalid_variable_as_name(self):
        component.registry.register(name="test", component=SimpleComponent)

        simple_tag_template = """
            {% load viewcomponent_tags %}
            {% with component_name="BLAHONGA" %}
                {% component component_name variable="variable" %}{% endcomponent %}
            {% endwith %}
        """
        template = Template(simple_tag_template)

        with pytest.raises(django_viewcomponent.component_registry.NotRegistered):
            template.render(Context({}))

    def test_call_component_with_two_variables(self):
        component.registry.register(name="test", component=IfVariableComponent)

        simple_tag_template = """
            {% load viewcomponent_tags %}
            {% component "test" variable="variable" variable2="hej" %}{% endcomponent %}
        """
        template = Template(simple_tag_template)

        rendered = template.render(Context({}))
        expected_outcome = (
            """Variable: <strong>variable</strong>\n"""
            """Variable2: <strong>hej</strong>"""
        )
        assert_dom_equal(expected_outcome, rendered)


class TestComponentSlotsTemplateTag:
    def test_slotted_template_basic(self):
        component.registry.register(name="test1", component=SlottedComponent)
        component.registry.register(name="test2", component=SimpleComponent)

        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component "test1" as component %}
                {% call component.header %}
                    Custom header
                {% endcall %}
                {% call component.main %}
                    {% component "test2" variable="variable" %}{% endcomponent %}
                {% endcall %}
            {% endcomponent %}
        """
        )
        rendered = template.render(Context({}))

        assert_dom_equal(
            rendered,
            """
            <custom-template>
                <header>Custom header</header>
                <main>Variable: <strong>variable</strong></main>
                <footer>Default footer</footer>
            </custom-template>
        """,
        )

    def test_slotted_template_with_context_var(self):
        component.registry.register(name="test1", component=SlottedComponentWithContext)

        template = Template(
            """
            {% load viewcomponent_tags %}
            {% with my_first_variable="test123" %}
                {% component "test1" variable="test456" as component %}
                    {% call component.main %}
                        {{ my_first_variable }} - {{ variable }}
                    {% endcall %}
                    {% call component.footer %}
                        {{ my_second_variable }}
                    {% endcall %}
                {% endcomponent %}
            {% endwith %}
        """
        )
        rendered = template.render(Context({"my_second_variable": "test321"}))

        assert_dom_equal(
            rendered,
            """
            <custom-template>
                <header>Default header</header>
                <main>test123 - test456</main>
                <footer>test321</footer>
            </custom-template>
        """,
        )

    def test_slotted_template_that_uses_missing_variable(self):
        component.registry.register(
            name="test", component=SlottedComponentWithMissingVariable
        )
        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component 'test' %}{% endcomponent %}
            """
        )
        rendered = template.render(Context({}))

        assert_dom_equal(
            """
            <custom-template>
                <header>Default header</header>
                <main>Default main</main>
                <footer>Default footer</footer>
            </custom-template>
            """,
            rendered,
        )

    def test_slotted_template_no_slots_filled(self):
        component.registry.register(name="test", component=SlottedComponent)

        template = Template(
            '{% load viewcomponent_tags %}{% component "test" %}{% endcomponent %}'
        )
        rendered = template.render(Context({}))

        assert_dom_equal(
            """
            <custom-template>
                <header>Default header</header>
                <main>Default main</main>
                <footer>Default footer</footer>
            </custom-template>
            """,
            rendered,
        )

    def test_slotted_template_without_slots(self):
        component.registry.register(name="test", component=SlottedComponentNoSlots)
        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component "test" %}{% endcomponent %}
        """
        )
        rendered = template.render(Context({}))

        assert_dom_equal("<custom-template></custom-template>", rendered)

    def test_slotted_template_without_slots_and_single_quotes(self):
        component.registry.register(name="test", component=SlottedComponentNoSlots)
        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component 'test' %}{% endcomponent %}
        """
        )
        rendered = template.render(Context({}))

        assert_dom_equal("<custom-template></custom-template>", rendered)

    def test_missing_required_slot_raises_error(self):
        class Component(component.Component):
            title = RendersOneField(required=True)

            template = "<div>{{ self.title.value }}</div>"

        component.registry.register("test", Component)
        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component 'test' %}
            {% endcomponent %}
            """
        )
        with pytest.raises(ValueError):
            template.render(Context({}))

    def test_fill_tag_can_occur_within_component_nested_with_content(
        self,
    ):
        class Component(component.Component):
            template = "<div>{{ self.content }}</div>"

        component.registry.register("test", Component)
        component.registry.register("slotted", SlottedComponent)

        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component 'test' as component_1 %}
              {% component "slotted" as component_2 %}
                {% call component_2.header %}This Is Allowed{% endcall %}
                {% call component_2.main %}{% endcall %}
                {% call component_2.footer %}{% endcall %}
              {% endcomponent %}
            {% endcomponent %}
            """
        )
        expected = """
        <div>
          <custom-template>
            <header>This Is Allowed</header>
            <main></main>
            <footer></footer>
          </custom-template>
        </div>
        """
        rendered = template.render(Context({}))
        assert_dom_equal(expected, rendered)


class TestMultiComponentSlots:
    def register_components(self):
        component.registry.register("first_component", SlottedComponent)
        component.registry.register("second_component", SlottedComponentWithContext)

    def make_template(self, first_component_slot="", second_component_slot=""):
        return Template(
            "{% load viewcomponent_tags %}"
            "{% component 'first_component' as component_1 %}"
            + first_component_slot
            + "{% endcomponent %}"
            "{% component 'second_component' variable='xyz' as component_2 %}"
            + second_component_slot
            + "{% endcomponent %}"
        )

    def expected_result(self, first_component_slot="", second_component_slot=""):
        return (
            "<custom-template><header>{}</header>".format(
                first_component_slot or "Default header"
            )
            + "<main>Default main</main><footer>Default footer</footer></custom-template>"
            + "<custom-template><header>{}</header>".format(
                second_component_slot or "Default header"
            )
            + "<main>Default main</main><footer>Default footer</footer></custom-template>"
        )

    def wrap_with_slot_tags(self, field, s):
        return f"{{% call {field} %}}" + s + "{% endcall %}"

    def test_both_components_render_correctly_with_no_slots(self):
        self.register_components()
        rendered = self.make_template().render(Context({}))
        assert_dom_equal(self.expected_result(), rendered)

    def test_both_components_render_correctly_with_slots(self):
        self.register_components()
        first_slot_content = "<p>Slot #1</p>"
        second_slot_content = "<div>Slot #2</div>"
        first_slot = self.wrap_with_slot_tags("component_1.header", first_slot_content)
        second_slot = self.wrap_with_slot_tags(
            "component_2.header", second_slot_content
        )
        rendered = self.make_template(first_slot, second_slot).render(Context({}))
        assert_dom_equal(
            self.expected_result(first_slot_content, second_slot_content), rendered
        )

    def test_both_components_render_correctly_when_only_first_has_slots(self):
        self.register_components()
        first_slot_content = "<p>Slot #1</p>"
        first_slot = self.wrap_with_slot_tags("component_1.header", first_slot_content)
        rendered = self.make_template(first_slot).render(Context({}))
        assert_dom_equal(self.expected_result(first_slot_content), rendered)

    def test_both_components_render_correctly_when_only_second_has_slots(self):
        self.register_components()
        second_slot_content = "<div>Slot #2</div>"
        second_slot = self.wrap_with_slot_tags(
            "component_2.header", second_slot_content
        )
        rendered = self.make_template("", second_slot).render(Context({}))
        assert_dom_equal(self.expected_result("", second_slot_content), rendered)


class TestNestedSlot:
    class NestedComponent(component.Component):
        outer = RendersOneField()
        inner = RendersOneField()

        template_name = "nested_slot_template.html"

    def test_default_slot_contents_render_correctly(self):
        component.registry.register("test", self.NestedComponent)

        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component 'test' %}{% endcomponent %}
        """
        )
        rendered = template.render(Context({}))
        assert_dom_equal(rendered, '<div id="outer">Default</div>')

    def test_inner_slot_overriden(self):
        component.registry.register("test", self.NestedComponent)

        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component 'test' as component %}{% call component.inner %}Override{% endcall %}{% endcomponent %}
        """
        )
        rendered = template.render(Context({}))
        assert_dom_equal(rendered, '<div id="outer">Override</div>')

    def test_outer_slot_overriden(self):
        component.registry.register("test", self.NestedComponent)

        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component 'test' as component %}{% call component.outer %}<p>Override</p>{% endcall %}{% endcomponent %}
        """
        )
        rendered = template.render(Context({}))
        assert_dom_equal(rendered, "<p>Override</p>")

    def test_both_overriden_and_inner_removed(self):
        component.registry.register("test", self.NestedComponent)

        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component 'test' as component %}
                {% call component.outer %}<p>Override</p>{% endcall %}
                {% call component.inner %}<p>Will not appear</p>{% endcall %}
            {% endcomponent %}
        """
        )
        rendered = template.render(Context({}))
        assert_dom_equal(rendered, "<p>Override</p>")


class TestConditionalSlot:
    class ConditionalComponent(component.Component):
        slot_a = RendersOneField()
        slot_b = RendersOneField()

        template_name = "conditional_template.html"

        def __init__(self, branch=None, **kwargs):
            self.branch = branch

    def test_no_content_if_branches_are_false(self):
        component.registry.register("test", self.ConditionalComponent)

        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component 'test' as component %}
                {% call component.slot_a %}Override A{% endcall %}
                {% call component.slot_b %}Override B{% endcall %}
            {% endcomponent %}
        """
        )
        rendered = template.render(Context({}))
        assert_dom_equal(rendered, "")

    def test_default_content_if_no_slots(self):
        component.registry.register("test", self.ConditionalComponent)

        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component 'test' branch='a' %}{% endcomponent %}
            {% component 'test' branch='b' %}{% endcomponent %}
        """
        )
        rendered = template.render(Context({}))
        assert_dom_equal(rendered, '<p id="a">Default A</p><p id="b">Default B</p>')

    def test_one_slot_overridden(self):
        component.registry.register("test", self.ConditionalComponent)

        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component 'test' branch='a' as component_1 %}
                {% call component_1.slot_b %}Override B{% endcall %}
            {% endcomponent %}
            {% component 'test' branch='b' as component_2 %}
                {% call component_2.slot_b %}Override B{% endcall %}
            {% endcomponent %}
        """
        )
        rendered = template.render(Context({}))
        assert_dom_equal(rendered, '<p id="a">Default A</p><p id="b">Override B</p>')

    def test_both_slots_overridden(self):
        component.registry.register("test", self.ConditionalComponent)

        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component 'test' branch='a' as component_1 %}
                {% call component_1.slot_a %}Override A{% endcall %}
                {% call component_1.slot_b %}Override B{% endcall %}
            {% endcomponent %}
            {% component 'test' branch='b' as component_2 %}
                {% call component_2.slot_a %}Override A{% endcall %}
                {% call component_2.slot_b %}Override B{% endcall %}
            {% endcomponent %}
        """
        )
        rendered = template.render(Context({}))
        assert_dom_equal(rendered, '<p id="a">Override A</p><p id="b">Override B</p>')


class TestTemplateSyntaxError:
    @pytest.fixture(autouse=True)
    def register_component(self):
        component.registry.register("test", SlottedComponent)

    def test_variable(self):
        Template(
            """
            {% load viewcomponent_tags %}
            {% component "test" %}
                {{ anything }}
            {% endcomponent %}
            """
        )

    def test_text(self):
        Template(
            """
            {% load viewcomponent_tags %}
            {% component "test" %}
                Text
            {% endcomponent %}
            """
        )

    def test_block_outside_call(self):
        Template(
            """
            {% load viewcomponent_tags %}
            {% component "test" as component %}
                {% if True %}
                    {% call component.header %}{% endcall %}
                {% endif %}
            {% endcomponent %}
        """
        )

    def test_unclosed_component_is_error(self):
        with pytest.raises(TemplateSyntaxError):
            Template(
                """
                {% load viewcomponent_tags %}
                {% component "test" %}
                {% call "header" %}{% endcall %}
            """
            )

    def test_fill_with_no_component_is_error(self):
        with pytest.raises(ValueError):
            Template(
                """
                {% load viewcomponent_tags %}
                {% call component.header %}contents{% endcall %}
            """
            ).render(Context({}))


class TestComponentNesting:
    @pytest.fixture(autouse=True)
    def register_component(self):
        component.registry.register("calendar", CalendarComponent)
        component.registry.register("dashboard", DashboardComponent)

    def test_component_nesting_component_without_fill(self):
        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component "dashboard" as component %}
                {% call component.header %}
                    Hello, User X
                {% endcall %}
            {% endcomponent %}
            """
        )
        rendered = template.render(Context({"items": [1, 2, 3]}))
        expected = """
        <div class="dashboard-component">
          <div class="calendar-component">
            <h1>
              Hello, User X
            </h1>
            <main>
              Here are your to-do items for today:
            </main>
          </div>
          <ol>
            <li>1</li>
            <li>2</li>
            <li>3</li>
          </ol>
        </div>
        """
        assert_dom_equal(rendered, expected)


class TestConditionalIfFilledSlots:
    class ComponentWithConditionalSlots(component.Component):
        title = RendersOneField()
        subtitle = RendersOneField()

        template_name = "template_with_conditional_slots.html"

    class ComponentWithComplexConditionalSlots(component.Component):
        title = RendersOneField()
        subtitle = RendersOneField()
        alt_subtitle = RendersOneField()

        template_name = "template_with_if_elif_else_conditional_slots.html"

    @pytest.fixture(autouse=True)
    def register_component(self):
        component.registry.register(
            "conditional_slots", self.ComponentWithConditionalSlots
        )
        component.registry.register(
            "complex_conditional_slots",
            self.ComponentWithComplexConditionalSlots,
        )

    def test_simple_component_with_conditional_slot(self):
        template = """
        {% load viewcomponent_tags %}
        {% component "conditional_slots" %}{% endcomponent %}
        """
        expected = """
        <div class="frontmatter-component">
          <div class="title">
          Title
          </div>
        </div>
        """
        rendered = Template(template).render(Context({}))
        assert_dom_equal(rendered, expected)

    def test_component_with_filled_conditional_slot(self):
        template = """
        {% load viewcomponent_tags %}
        {% component "conditional_slots" as component %}
          {% call component.subtitle %} My subtitle {% endcall %}
        {% endcomponent %}
        """
        expected = """
        <div class="frontmatter-component">
          <div class="title">
          Title
          </div>
          <div class="subtitle">
            My subtitle
          </div>
        </div>
        """
        rendered = Template(template).render(Context({}))
        assert_dom_equal(rendered, expected)

    def test_elif_of_complex_conditional_slots(self):
        template = """
        {% load viewcomponent_tags %}
        {% component "complex_conditional_slots" as component %}
            {% call component.alt_subtitle %} A different subtitle {% endcall %}
        {% endcomponent %}
        """
        expected = """
           <div class="frontmatter-component">
             <div class="title">
             Title
             </div>
             <div class="subtitle">
             A different subtitle
             </div>
           </div>
        """
        rendered = Template(template).render(Context({}))
        assert_dom_equal(rendered, expected)

    def test_else_of_complex_conditional_slots(self):
        template = """
           {% load viewcomponent_tags %}
           {% component "complex_conditional_slots" %}
           {% endcomponent %}
        """
        expected = """
           <div class="frontmatter-component">
             <div class="title">
             Title
             </div>
            <div class="warning">Nothing filled!</div>
           </div>
        """
        rendered = Template(template).render(Context({}))
        assert_dom_equal(rendered, expected)


class TestComponentWithinBlock:
    def test_block_and_extends_tag_works(self):
        component.registry.register("slotted_component", SlottedComponent)
        template = """
        {% extends "extendable_template_with_blocks.html" %}
        {% load viewcomponent_tags %}
        {% block body %}
          {% component "slotted_component" as component %}
            {% call component.header %}{% endcall %}
            {% call component.main %}
              TEST
            {% endcall %}
            {% call component.footer %}{% endcall %}
          {% endcomponent %}
        {% endblock %}
        """
        rendered = Template(template).render(Context())
        expected = """
        <!DOCTYPE html>
        <html lang="en">
        <body>
        <main role="main">
          <div class='container main-container'>
            <custom-template>
              <header></header>
              <main>TEST</main>
              <footer></footer>
            </custom-template>
          </div>
        </main>
        </body>
        </html>
        """
        assert_dom_equal(rendered, expected)


class TestComponentCollectionSlots:
    class TabsComponent(component.Component):
        tabs = RendersManyField(required=True)
        panels = RendersManyField(required=True)

        template = """
        <div>
            {% for tab in self.tabs.value %}
                <div class="tab">
                    {{ tab }}
                </div>
            {% endfor %}
        </div>

        <div>
            {% for panel in self.panels.value %}
                <div class="panel">
                    {{ panel }}
                </div>
            {% endfor %}
        </div>
        """

    @pytest.fixture(autouse=True)
    def register_component(self):
        component.registry.register("tabs", self.TabsComponent)

    def test_missing_required_slot_raises_error(self):
        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component 'tabs' %}
            {% endcomponent %}
            """
        )
        with pytest.raises(ValueError):
            template.render(Context({}))

    def test_collection_basic(self):
        template = Template(
            """
            {% load viewcomponent_tags %}
            {% component 'tabs' as component %}
                {% call component.tabs %}Tab 1{% endcall %}
                {% call component.tabs %}Tab 2{% endcall %}
                {% call component.tabs %}Tab 3{% endcall %}

                {% call component.panels %}Panel 1{% endcall %}
                {% call component.panels %}Panel 2{% endcall %}
                {% call component.panels %}Panel 3{% endcall %}
            {% endcomponent %}
            """
        )
        rendered = template.render(Context({}))
        assert_dom_equal(
            """
<div>
    <div class="tab">
        Tab 1
    </div>
    <div class="tab">
        Tab 2
    </div>
    <div class="tab">
        Tab 3
    </div>
</div>

<div>
    <div class="panel">
        Panel 1
    </div>
    <div class="panel">
        Panel 2
    </div>
    <div class="panel">
        Panel 3
    </div>
</div>
            """,
            rendered,
        )

    def test_collection_variable(self):
        template = Template(
            """
            {% load viewcomponent_tags %}
            {% with tab="Tab" panel="Panel" %}
            {% component 'tabs' as component %}
                {% call component.tabs %}{{ tab }} 1{% endcall %}
                {% call component.tabs %}{{ tab }} 2{% endcall %}
                {% call component.tabs %}{{ tab }} 3{% endcall %}

                {% call component.panels %}{{ panel }} 1{% endcall %}
                {% call component.panels %}{{ panel }} 2{% endcall %}
                {% call component.panels %}{{ panel }} 3{% endcall %}
            {% endcomponent %}
            {% endwith %}
            """
        )
        rendered = template.render(Context({}))
        assert_dom_equal(
            """
<div>
    <div class="tab">
        Tab 1
    </div>
    <div class="tab">
        Tab 2
    </div>
    <div class="tab">
        Tab 3
    </div>
</div>

<div>
    <div class="panel">
        Panel 1
    </div>
    <div class="panel">
        Panel 2
    </div>
    <div class="panel">
        Panel 3
    </div>
</div>
            """,
            rendered,
        )


@pytest.mark.django_db
class TestFieldComponentParameter:
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
