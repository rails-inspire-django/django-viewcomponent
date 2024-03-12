import pytest
from django.template import Context, Template

from django_viewcomponent import component
from django_viewcomponent.fields import RendersOneField
from tests.utils import assert_dom_equal


class ChildComponent(component.Component):
    title = RendersOneField()

    template = """
    <div>{{ variable }}</div>
    <div>{{ self.title.value }}</div>
    """


class ParentComponent(component.Component):
    template = """
    {% load viewcomponent_tags %}
    {% component "child" as component %}
        {% call component.title %}
            {{ variable }}
        {% endcall %}
    {% endcomponent %}
    """

    def __init__(self, variable=None, **kwargs):
        self.variable = variable

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.variable:
            # add extra context data so child component can access it
            context["variable"] = self.variable
        return context


class TestContextBehavior:
    @pytest.fixture(autouse=True)
    def register_component(self):
        component.registry.register("parent", ParentComponent)
        component.registry.register("child", ChildComponent)

    def test_context(self):
        template = """
        {% load viewcomponent_tags %}
        {% with variable="test123" %}
          {% component "parent" %}
          {% endcomponent %}
        {% endwith %}
        """
        rendered = Template(template).render(Context())
        expected = """
        <div>test123</div>
        <div>test123</div>
        """
        assert_dom_equal(rendered, expected)

    def test_context_overwrite(self):
        """
        Parent component overwrite the context variable in the get_context_data method
        """
        template = """
        {% load viewcomponent_tags %}
        {% with variable="test123" %}
          {% component "parent" variable="test456" %}
          {% endcomponent %}
        {% endwith %}
        """
        rendered = Template(template).render(Context())
        expected = """
        <div>test456</div>
        <div>test456</div>
        """
        assert_dom_equal(rendered, expected)
