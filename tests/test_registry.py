import pytest

from django_viewcomponent import component


@pytest.fixture
def registry():
    return component.ComponentRegistry()


class MockComponent(component.Component):
    pass


class MockComponent2(component.Component):
    pass


class MockComponentView(component.Component):
    def get(self, request, *args, **kwargs):
        pass


def test_register_class_decorator(registry):
    @component.register("decorated_component")
    class TestComponent(component.Component):
        pass

    assert component.registry.get("decorated_component") == TestComponent


def test_simple_register(registry):
    registry.register(name="testcomponent", component=MockComponent)
    assert registry.all() == {"testcomponent": MockComponent}


def test_register_two_components(registry):
    registry.register(name="testcomponent", component=MockComponent)
    registry.register(name="testcomponent2", component=MockComponent)
    assert registry.all() == {
        "testcomponent": MockComponent,
        "testcomponent2": MockComponent,
    }


def test_prevent_registering_different_components_with_the_same_name(registry):
    registry.register(name="testcomponent", component=MockComponent)
    with pytest.raises(component.AlreadyRegistered):
        registry.register(name="testcomponent", component=MockComponent2)


def test_allow_duplicated_registration_of_the_same_component(registry):
    try:
        registry.register(name="testcomponent", component=MockComponentView)
        registry.register(name="testcomponent", component=MockComponentView)
    except component.AlreadyRegistered:
        pytest.fail("Should not raise AlreadyRegistered")


def test_simple_unregister(registry):
    registry.register(name="testcomponent", component=MockComponent)
    registry.unregister(name="testcomponent")
    assert registry.all() == {}


def test_raises_on_failed_unregister(registry):
    with pytest.raises(component.NotRegistered):
        registry.unregister(name="testcomponent")
