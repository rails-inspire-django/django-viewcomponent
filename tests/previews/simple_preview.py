from django_viewcomponent.preview import ViewComponentPreview
from django.template import Context, Template
from django_viewcomponent import component


@component.register("example")
class ExampleComponent(component.Component):
    template = """
        <span title="{{ self.title }}">
          {{ self.content }}
        </span> 
    """

    def __init__(self, **kwargs):
        self.title = kwargs['title']


class SimpleExampleComponentPreview(ViewComponentPreview):

    def with_title(self, title="default title", **kwargs):
        return title

    def with_component_call(self, title="default title", **kwargs):
        """
        We can initialize the component and call render() method
        """
        comp = ExampleComponent(title=title)
        return comp.render(comp.get_context_data())

    def with_template_render(self, title="default title", **kwargs):
        """
        We can initialize the component in the template
        """
        template = Template(
            """
            {% load viewcomponent_tags %}
            
            {% component "example" title=title %}
            {% endcomponent %}
        """
        )

        # pass the title from the URL querystring to the context
        return template.render(Context({"title": title}))
