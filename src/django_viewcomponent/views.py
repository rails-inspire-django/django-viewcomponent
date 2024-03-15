from django_viewcomponent.preview import ViewComponentPreview
from django.shortcuts import render


def request_get_to_dict(request):
    """
    Convert request.GET to a dictionary
    """
    query_dict = request.GET
    return {key: query_dict.getlist(key) if len(query_dict.getlist(key)) > 1 else query_dict.get(key) for key in query_dict.keys()}


def preview_index_view(request):
    previews = ViewComponentPreview.previews
    context = {
        'previews': previews
    }
    return render(request, 'view_components/index.html', context)


def previews_view(request, preview_name):
    preview = ViewComponentPreview.previews[preview_name]
    context = {
        'preview': preview
    }
    return render(request, 'view_components/previews.html', context)


def preview_view(request, preview_name, example_name):
    preview_cls = ViewComponentPreview.previews[preview_name]
    preview_instance = preview_cls()

    query_dict = request_get_to_dict(request)
    fun = getattr(preview_instance, example_name)
    preview_html = fun(**query_dict)
    preview_source = preview_instance.preview_source(example_name)

    context = {
        'preview_instance': preview_instance,
        'preview_html': preview_html,
        'preview_source': preview_source,
    }

    return render(request, 'view_components/preview.html', context)
