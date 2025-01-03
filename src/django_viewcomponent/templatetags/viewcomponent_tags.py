from typing import Type

import django.template
from django.template import Context
from django.template.base import FilterExpression, Node, NodeList
from django.template.exceptions import TemplateSyntaxError
from django.template.library import parse_bits

from django_viewcomponent.component import Component
from django_viewcomponent.component_registry import registry as component_registry
from django_viewcomponent.fields import BaseSlotField

register = django.template.Library()


@register.tag("call")
def do_call(parser, token):
    bits = token.split_contents()
    tag_name = "call"
    tag_args, tag_kwargs = parse_bits(
        parser=parser,
        bits=bits,
        params=[],
        takes_context=False,
        name=tag_name,
        varargs=True,
        varkw=[],
        defaults=None,
        kwonly=[],
        kwonly_defaults=None,
    )

    if len(tag_args) > 1:
        # At least one position arg, so take the first as the component name
        args = tag_args[1:]
        kwargs = tag_kwargs
    else:
        raise TemplateSyntaxError(f"Syntax error in '{tag_name}' tag")

    nodelist = parser.parse(parse_until=["endcall"])
    parser.delete_first_token()

    return CallNode(
        parser=parser,
        nodelist=nodelist,
        args=args,
        kwargs=kwargs,
    )


class CallNode(Node):
    def __init__(
        self,
        parser,
        nodelist: NodeList,
        args,
        kwargs,
    ):
        self.parser = parser
        self.nodelist: NodeList = nodelist
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        raise NotImplementedError

    def render(self, context):
        resolved_kwargs = {
            key: safe_resolve(kwarg, context) for key, kwarg in self.kwargs.items()
        }

        if "content" in resolved_kwargs:
            raise ValueError(
                "The 'content' kwarg is reserved and cannot be passed in component call tag",
            )

        resolved_kwargs["nodelist"] = self.nodelist
        resolved_kwargs["context"] = context

        component_token, field_token = self.args[0].token.split(".")
        component_instance = FilterExpression(component_token, self.parser).resolve(
            context,
        )
        if not component_instance:
            raise ValueError(f"Component {component_token} not found in context")

        available_slot_fields_map = {}
        # iterate all attributes of the component instance and add the BaseSlotField to the list
        for field_name in dir(component_instance):
            field = getattr(component_instance, field_name)
            if isinstance(field, BaseSlotField):
                types = field.types
                if types:
                    for polymorphic_type in types:
                        available_slot_fields_map[
                            f"{field_name}_{polymorphic_type}"
                        ] = [field, polymorphic_type]
                else:
                    available_slot_fields_map[field_name] = [field, None]

        if field_token not in available_slot_fields_map:
            raise ValueError(
                f"Field {field_token} not found in component {component_token}",
            )

        field, polymorphic_type = available_slot_fields_map[field_token]
        resolved_kwargs["polymorphic_type"] = polymorphic_type

        return field.handle_call(**resolved_kwargs) or ""


class ComponentNode(Node):
    def __init__(
        self,
        name_fexp: FilterExpression,
        context_args,
        context_kwargs,
        nodelist: NodeList,
        target_var=None,
    ):
        self.name_fexp = name_fexp
        self.context_args = context_args or []
        self.context_kwargs = context_kwargs or {}
        self.nodelist = nodelist
        self.target_var = target_var

    def __repr__(self):
        return "<ComponentNode: %s. Contents: %r>" % (
            self.name_fexp,
            getattr(
                self,
                "nodelist",
                None,
            ),  # 'nodelist' attribute only assigned later.
        )

    def render(self, context: Context):
        resolved_component_name = self.name_fexp.resolve(context)

        # get component class
        component_cls: Type[Component] = component_registry.get(resolved_component_name)

        # Resolve FilterExpressions and Variables that were passed as args to the
        # component, then call component's context method
        # to get values to insert into the context
        resolved_component_args = [
            safe_resolve(arg, context) for arg in self.context_args
        ]
        resolved_component_kwargs = {
            key: safe_resolve(kwarg, context)
            for key, kwarg in self.context_kwargs.items()
        }

        # create component
        component: Component = component_cls(
            *resolved_component_args,
            **resolved_component_kwargs,
        )
        component.component_target_var = self.target_var
        component.component_context = context

        # https://docs.djangoproject.com/en/5.1/ref/templates/api/#django.template.Context.push
        with component.component_context.push():
            # developer can add extra context data in this method
            updated_context = component.get_context_data()

            # create slot fields
            component.create_slot_fields()

            # render children nodelist
            component.content = self.nodelist.render(updated_context)

            component.check_slot_fields()

            return component.render(updated_context)


@register.tag(name="component")
def do_component(parser, token):
    """
    To give the component access to the template context:
        {% component "name" positional_arg keyword_arg=value ... %}

    To render the component in an isolated context:
        {% component "name" positional_arg keyword_arg=value ... only %}

    Positional and keyword arguments can be literals or template variables.
    The component name must be a single- or double-quotes string and must
    be either the first positional argument or, if there are no positional
    arguments, passed as 'name'.
    """

    bits = token.split_contents()

    # check as keyword
    target_var = None
    if len(bits) >= 4 and bits[-2] == "as":
        target_var = bits[-1]
        bits = bits[:-2]

    component_name, context_args, context_kwargs = parse_component_with_arguments(
        parser,
        bits,
        "component",
    )
    nodelist: NodeList = parser.parse(parse_until=["endcomponent"])
    parser.delete_first_token()

    component_node = ComponentNode(
        name_fexp=FilterExpression(component_name, parser),
        context_args=context_args,
        context_kwargs=context_kwargs,
        nodelist=nodelist,
        target_var=target_var,
    )

    return component_node


def parse_component_with_arguments(parser, bits, tag_name):
    tag_args, tag_kwargs = parse_bits(
        parser=parser,
        bits=bits,
        params=["tag_name", "name"],
        takes_context=False,
        name=tag_name,
        varargs=True,
        varkw=[],
        defaults=None,
        kwonly=[],
        kwonly_defaults=None,
    )

    if tag_name != tag_args[0].token:
        raise RuntimeError(
            f"Internal error: Expected tag_name to be {tag_name}, but it was {tag_args[0].token}",
        )
    if len(tag_args) > 1:
        # At least one position arg, so take the first as the component name
        component_name = tag_args[1].token
        context_args = tag_args[2:]
        context_kwargs = tag_kwargs
    else:
        raise TemplateSyntaxError(
            f"Call the '{tag_name}' tag with a component name as the first parameter",
        )

    return component_name, context_args, context_kwargs


def safe_resolve(context_item, context):
    """Resolve FilterExpressions and Variables in context if possible.  Return other items unchanged."""

    return (
        context_item.resolve(context)
        if hasattr(context_item, "resolve")
        else context_item
    )
