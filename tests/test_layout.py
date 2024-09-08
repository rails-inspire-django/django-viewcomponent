from tests.testapp.layout import HTML, Button, Div

from .utils import assert_select


class TestLayoutComponents:
    def test_html(self):
        html = HTML("{% if saved %}Data saved{% endif %}").render_from_parent_context(
            {"saved": True}
        )
        assert "Data saved" in html

        # step_field and step0 not defined
        html = HTML(
            '<input type="hidden" name="{{ step_field }}" value="{{ step0 }}" />'
        ).render_from_parent_context()
        assert_select(html, "input")

    def test_div(self):
        html = Div(
            Div(
                HTML("Hello {{ value_1 }}"),
                HTML("Hello {{ value_2 }}"),
                css_class="wrapper",
            ),
            dom_id="main",
        ).render_from_parent_context({"value_1": "world"})

        assert_select(html, "div#main")
        assert_select(html, "div.wrapper")
        assert "Hello world" in html

    def test_button(self):
        html = Div(
            Div(
                Button("{{ value_1 }}", css_class="btn btn-primary"),
            ),
            dom_id="main",
        ).render_from_parent_context({"value_1": "world"})

        assert_select(html, "button.btn")
        assert_select(html, "button[type=button]")
        assert "world" in html
