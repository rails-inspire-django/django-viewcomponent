from django_viewcomponent.component_registry import registry as component_registry


class FieldValue:
    def __init__(
        self,
        nodelist,
        field_context,
        polymorphic_type,
        polymorphic_types,
        dict_data: dict,
        component: None,
        parent_component=None,
    ):
        self._nodelist = nodelist
        self._field_context = field_context
        self._polymorphic_type = polymorphic_type
        self._polymorphic_types = polymorphic_types
        self._dict_data = dict_data
        self._component = component
        self._parent_component = parent_component

    def __str__(self):
        return self.render()

    def render(self):
        if self._polymorphic_types:
            component_expression = self._polymorphic_types[self._polymorphic_type]
            return self._render(component_expression)
        else:
            component_expression = self._component
            return self._render(component_expression)

    def _render(self, target):
        from django_viewcomponent.component import Component

        if isinstance(target, str):
            return self._render_for_component_cls(
                component_registry.get(target),
            )
        elif not isinstance(target, type) and callable(target):
            # target is function
            callable_component = target
            content = self._nodelist.render(self._field_context)
            result = callable_component(
                self=self._parent_component,
                content=content,
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
        elif isinstance(target, type) and issubclass(
            target,
            Component,
        ):
            # target is Component class
            return self._render_for_component_cls(target)
        elif target is None:
            return self._nodelist.render(self._field_context)
        else:
            raise ValueError(f"Invalid component variable {target}")

    def _render_for_component_cls(self, component_cls):
        component = component_cls(
            **self._dict_data,
        )

        return self._render_for_component_instance(component)

    def _render_for_component_instance(self, component):
        component.component_context = self._field_context

        with component.component_context.push():
            # create slot fields
            component.create_slot_fields()

            # render content first
            component.content = self._nodelist.render(component.component_context)

            component.check_slot_fields()

            updated_context = component.get_context_data()

            return component.render(updated_context)


class BaseSlotField:
    parent_component = None

    def __init__(self, required=False, component=None, types=None, **kwargs):
        self._value = None
        self._filled = False
        self._required = required
        self._component = component
        self._types = types

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

    @property
    def types(self):
        return self._types

    def handle_call(self, nodelist, context, polymorphic_type, **kwargs):
        raise NotImplementedError("You must implement the `handle_call` method.")


class RendersOneField(BaseSlotField):
    def handle_call(self, nodelist, context, polymorphic_type, **kwargs):
        value_instance = FieldValue(
            nodelist=nodelist,
            field_context=context,
            polymorphic_type=polymorphic_type,
            polymorphic_types=self.types,
            dict_data={**kwargs},
            component=self._component,
            parent_component=self.parent_component,
        )

        self._value = value_instance.render()
        self._filled = True


class FieldValueListWrapper:
    def __init__(self):
        self.data = []

    def append(self, value):
        self.data.append(value)

    def __iter__(self):
        yield from self.data


class RendersManyField(BaseSlotField):
    def handle_call(self, nodelist, context, polymorphic_type, **kwargs):
        value_instance = FieldValue(
            nodelist=nodelist,
            field_context=context,
            polymorphic_type=polymorphic_type,
            polymorphic_types=self.types,
            dict_data={**kwargs},
            component=self._component,
            parent_component=self.parent_component,
        )

        if self._value is None:
            self._value = FieldValueListWrapper()

        self._value.append(value_instance.render())
        self._filled = True
