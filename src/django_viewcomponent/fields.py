from django_viewcomponent.component_registry import registry as component_registry


class FieldValue:
    def __init__(
        self,
        nodelist,
        dict_data: dict,
        component: None,
        parent_component=None,
    ):
        self._nodelist = nodelist
        self._dict_data = dict_data
        self._component = component
        self._parent_component = parent_component

    def __str__(self):
        return self.render()

    def render(self):
        from django_viewcomponent.component import Component

        if isinstance(self._component, str):
            return self._render_for_component_cls(
                component_registry.get(self._component),
            )
        elif not isinstance(self._component, type) and callable(self._component):
            # self._component is function
            callable_component = self._component
            result = callable_component(
                self=self._parent_component,
                **self._dict_data,
            )

            if isinstance(result, str):
                return result
            elif isinstance(result, Component):
                # render component instance
                return self._render_for_component_instance(result)
            else:
                raise ValueError(
                    f"Callable slot component must return str or Component instance. Got {result}",
                )
        elif isinstance(self._component, type) and issubclass(
            self._component,
            Component,
        ):
            # self._component is Component class
            return self._render_for_component_cls(self._component)
        elif self._component is None:
            return self._nodelist.render(self._parent_component.component_context)
        else:
            raise ValueError(f"Invalid component variable {self._component}")

    def _render_for_component_cls(self, component_cls):
        component = component_cls(
            **self._dict_data,
        )

        return self._render_for_component_instance(component)

    def _render_for_component_instance(self, component):
        component.component_context = self._parent_component.component_context

        with component.component_context.push():
            updated_context = component.get_context_data()

            # create slot fields
            component.create_slot_fields()

            component.content = self._nodelist.render(updated_context)

            component.check_slot_fields()

            return component.render(updated_context)


class BaseSlotField:
    parent_component = None

    def __init__(self, value=None, required=False, component=None, **kwargs):
        self._value = value
        self._filled = False
        self._required = required
        self._component = component

    @classmethod
    def initialize_fields(cls):
        cls.header = RendersOneField()
        cls.main = RendersOneField()
        cls.footer = RendersOneField()

    @property
    def value(self):
        return self._value

    @property
    def filled(self):
        return self._filled

    @property
    def required(self):
        return self._required

    def handle_call(self, nodelist, **kwargs):
        raise NotImplementedError("You must implement the `handle_call` method.")


class RendersOneField(BaseSlotField):
    def handle_call(self, nodelist, **kwargs):
        value_instance = FieldValue(
            nodelist=nodelist,
            dict_data={**kwargs},
            component=self._component,
            parent_component=self.parent_component,
        )

        self._filled = True
        self._value = value_instance


class FieldValueListWrapper:
    """
    This helps render FieldValue eagerly when component template has
    {% for panel in self.panels.value %}, this can avoid issues if `panel` of the for loop statement
    # override context variables in some cases.
    """

    def __init__(self):
        self.data = []

    def append(self, value):
        self.data.append(value)

    def __iter__(self):
        for field_value in self.data:
            yield field_value.render()


class RendersManyField(BaseSlotField):
    def handle_call(self, nodelist, **kwargs):
        value_instance = FieldValue(
            nodelist=nodelist,
            dict_data={**kwargs},
            component=self._component,
            parent_component=self.parent_component,
        )

        if self._value is None:
            self._value = FieldValueListWrapper()

        self._value.append(value_instance)
        self._filled = True
