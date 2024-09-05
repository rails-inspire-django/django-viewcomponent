from django_viewcomponent import component


@component.register("testapp.example")
class ExampleComponent(component.Component):
    template_name = "testapp/example/example.html"

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "World")
