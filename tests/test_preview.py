import pytest
from django_viewcomponent.preview import ViewComponentPreview
from django.urls import reverse


class TestBasicPreview:
    def test_setup(self):
        """
        In tests/conftest.py

        VIEW_COMPONENTS={
            "preview_base": ["previews"],
        },
        """
        assert len(ViewComponentPreview.previews.keys())

    def test_preview_index_view(self, client):
        response = client.get(reverse('django_viewcomponent:preview-index'))

        assert response.status_code == 200
        assert b"simple_example_component" in response.content
        assert b"with_title" in response.content

    def test_previews(self, client):
        response = client.get(reverse('django_viewcomponent:previews', kwargs={'preview_name': 'simple_example_component'}))

        assert response.status_code == 200
        assert b"with_title" in response.content

    def test_preview(self, client):
        response = client.get(reverse('django_viewcomponent:preview', kwargs={
            'preview_name': 'simple_example_component',
            'example_name': 'with_title',
        }))

        assert response.status_code == 200
        assert b"default title" in response.content

    def test_simple_preview_with_querystring(self, client):
        query_params = {'title': 'hello world'}
        response = client.get(reverse('django_viewcomponent:preview', kwargs={
            'preview_name': 'simple_example_component',
            'example_name': 'with_title',
        }), data=query_params)

        assert response.status_code == 200
        assert b"hello world" in response.content


class TestComponentPreview:

    def test_component_call(self, client):
        query_params = {'title': 'hello world'}
        response = client.get(reverse('django_viewcomponent:preview', kwargs={
            'preview_name': 'simple_example_component',
            'example_name': 'with_component_call',
        }), data=query_params)

        assert response.status_code == 200
        assert b'<span title="hello world">' in response.content

    def test_template_render(self, client):
        query_params = {'title': 'hello world'}
        response = client.get(reverse('django_viewcomponent:preview', kwargs={
            'preview_name': 'simple_example_component',
            'example_name': 'with_template_render',
        }), data=query_params)

        assert response.status_code == 200
        assert b'<span title="hello world">' in response.content
