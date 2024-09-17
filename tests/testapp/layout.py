from django.template import Template

from django_viewcomponent import component


class Div(component.Component):
    template_name = "layout/div.html"
    css_class = None

    def __init__(self, *fields, dom_id=None, css_class=None):
        self.fields = list(fields)
        if self.css_class and css_class:
            self.css_class += f" {css_class}"
        elif css_class:
            self.css_class = css_class
        self.dom_id = dom_id

    def get_context_data(self):
        context = super().get_context_data()
        self.fields_html = " ".join(
            [
                child_component.render_from_parent_context(context)
                for child_component in self.fields
            ],
        )
        return context


class HTML(component.Component):
    def __init__(self, html, **kwargs):
        self.html = html

    def get_template(self) -> Template:
        return Template(self.html)


class Button(component.Component):
    template_name = "layout/button.html"
    field_classes = "btn"
    button_type = "button"

    def __init__(self, text, dom_id=None, css_class=None, template=None):
        self.text = text

        if dom_id:
            self.id = dom_id

        self.attrs = {}

        if css_class:
            self.field_classes += f" {css_class}"

        self.template_name = template or self.template_name

    def get_context_data(self):
        context = super().get_context_data()
        self.text_html = Template(str(self.text)).render(context)
        return context
