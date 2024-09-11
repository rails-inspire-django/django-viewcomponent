from typing import Optional

from django_viewcomponent.component_registry import registry as component_registry


class FieldValue:
    def __init__(
        self,
        dict_data: dict,
        component: Optional[str] = None,
        parent_component=None,
        **kwargs
    ):
        self._dict_data = dict_data
        self._content = self._dict_data.pop("content", "")
        self._component = component
        self._parent_component = parent_component

    def __str__(self):
        if self._component is None:
            return self._content
        else:
            # If the slot field is defined with component, then we will use the component to render
            return self.render()

    def render(self):
        component_cls = component_registry.get(self._component)
        component = component_cls(
            **self._dict_data,
        )
        component.component_name = self._component
        component.component_context = self._parent_component.component_context

        with component.component_context.push():
            updated_context = component.get_context_data()

            # create slot fields
            component.create_slot_fields()

            component.content = self._content

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

    def handle_call(self, content, **kwargs):
        raise NotImplementedError("You must implement the `handle_call` method.")


class RendersOneField(BaseSlotField):
    def handle_call(self, content, **kwargs):
        value_dict = {
            "content": content,
            "parent_component": self.parent_component,
            **kwargs,
        }
        value_instance = FieldValue(
            dict_data=value_dict,
            component=self._component,
            parent_component=self.parent_component,
        )

        self._filled = True
        self._value = value_instance


class RendersManyField(BaseSlotField):
    def handle_call(self, content, **kwargs):
        value_dict = {
            "content": content,
            "parent_component": self.parent_component,
            **kwargs,
        }
        value_instance = FieldValue(
            dict_data=value_dict,
            component=self._component,
            parent_component=self.parent_component,
        )

        if self._value is None:
            self._value = []

        self._value.append(value_instance)
        self._filled = True
