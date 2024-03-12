import pytest
from django.core.exceptions import ImproperlyConfigured
from django.template import Context

from django_viewcomponent import component
from tests.utils import assert_dom_equal


class TestComponent:
    def test_component_require_template(self):
        """
        Component should raise ImproperlyConfigured if no template is provided.
        """

        class EmptyComponent(component.Component):
            pass

        with pytest.raises(ImproperlyConfigured):
            EmptyComponent().get_template()

    def test_component_args(self):
        """
        Pass arguments to component constructor, set it as instance attribute
        and get the value as {{ self.attribute }} in the template.
        """

        class SimpleComponent(component.Component):
            template = "<div>{{ self.size }}</div>"

            def __init__(self, size):
                self.size = size

        comp = SimpleComponent(size="sm")
        assert_dom_equal("<div>sm</div>", comp.render(comp.get_context_data()))

    def test_component_with_dynamic_template(self):
        """
        Overwrite get_template_name to return a dynamic template name.
        """

        class SvgComponent(component.Component):
            def __init__(self, name, css_class="", title="", **kwargs):
                self.name = name
                self.css_class = css_class
                self.title = title

            def get_template_name(self):
                return f"svg_{self.name}.svg"

        comp = SvgComponent(name="sun")
        assert_dom_equal("<svg>sun</svg>", comp.render(comp.get_context_data()))

        comp = SvgComponent(name="moon")
        assert_dom_equal("<svg>moon</svg>", comp.render(comp.get_context_data()))


class TestComponentContext:
    def test_component_outer_context(self):
        """
        Access outer context in the component template.
        """

        class SimpleComponent(component.Component):
            template = "<div>{{ variable }}</div>"

        comp = SimpleComponent()
        assert_dom_equal("<div>test</div>", comp.render({"variable": "test"}))

    def test_component_with_extra_context_variables(self):
        class FilteredComponent(component.Component):
            template = """
<div>{{ self.var1 }}</div>
<div>{{ var2 }}</div>
<div>{{ outer_variable }}</div>
            """

            def __init__(self, var1):
                self.var1 = var1

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context["var2"] = self.var1
                return context

        # ComponentNode do the same way
        comp = FilteredComponent(var1="test")
        view_context = Context({"outer_variable": "test"})
        comp.outer_context = view_context
        component_context = comp.get_context_data()

        assert_dom_equal(
            "<div>test</div><div>test</div><div>test</div>",
            comp.render(component_context),
        )
